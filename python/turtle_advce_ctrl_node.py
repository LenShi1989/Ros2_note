#!/usr/bin/env python3
import sys
import math
import threading

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, 
                             QDoubleSpinBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class Communicate(QObject):
    """用於背景 ROS 執行緒與 PyQt 主 UI 執行緒之間的安全的資料傳遞"""
    pose_signal = pyqtSignal(Pose)


class TurtleAdvanceCtrlNode(Node):
    """ROS 2 節點：同時包含 Publisher (cmd_vel) 與 Subscriber (pose)"""
    def __init__(self, comm: Communicate):
        super().__init__('turtle_advce_ctrl_node')
        self.comm = comm

        # 1. 建立 Publisher: 控制小烏龜速度
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 2. 建立 Subscriber: 訂閱小烏龜即時 Pose
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # 移動狀態變數 (1 表示前進/左轉, -1 表示後退/右轉, 0 表示停止)
        self.dir_linear = 0
        self.dir_angular = 0
        
        # 目標速度大小
        self.target_linear_speed = 2.0
        self.target_angular_speed = 1.5

        # 定時器：10Hz 持續發送控制命令
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('Turtle Advance Control Node 已成功啟動！')

    def pose_callback(self, msg: Pose):
        """接收到 Pose 消息後，發送 Qt Signal 更新 UI"""
        self.comm.pose_signal.emit(msg)

    def timer_callback(self):
        """定時發送 Twist 速度命令"""
        msg = Twist()
        msg.linear.x = float(self.dir_linear * self.target_linear_speed)
        msg.angular.z = float(self.dir_angular * self.target_angular_speed)
        self.publisher_.publish(msg)


class TurtleAdvanceWindow(QWidget):
    """PyQt5 高級圖形化介面"""
    def __init__(self, ros_node: TurtleAdvanceCtrlNode, comm: Communicate):
        super().__init__()
        self.ros_node = ros_node
        self.comm = comm
        
        # 連接 Signal 至 UI 更新槽函數
        self.comm.pose_signal.connect(self.update_pose_ui)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ROS 2 Turtle 高級控制器 (帶 Pose 監控)')
        self.resize(380, 420)

        # ------------------ 1. 即時數值顯示區塊 (Pose Dashboard) ------------------
        pose_group = QGroupBox("小烏龜即時狀態監視器")
        pose_grid = QGridLayout()

        self.lbl_x = QLabel("0.00")
        self.lbl_y = QLabel("0.00")
        self.lbl_linear_vel = QLabel("0.00 m/s")
        self.lbl_angular_vel = QLabel("0.00 rad/s")
        self.lbl_theta_deg = QLabel("0.00°")
        self.lbl_theta_rad = QLabel("0.00 rad")

        # 美化標籤樣式
        for lbl in [self.lbl_x, self.lbl_y, self.lbl_linear_vel, 
                    self.lbl_angular_vel, self.lbl_theta_deg, self.lbl_theta_rad]:
            lbl.setStyleSheet("font-weight: bold; color: #1976D2;")

        # 佈局配置
        pose_grid.addWidget(QLabel("當前 X 座標:"), 0, 0)
        pose_grid.addWidget(self.lbl_x, 0, 1)
        
        pose_grid.addWidget(QLabel("當前 Y 座標:"), 1, 0)
        pose_grid.addWidget(self.lbl_y, 1, 1)

        pose_grid.addWidget(QLabel("當前線速度:"), 2, 0)
        pose_grid.addWidget(self.lbl_linear_vel, 2, 1)

        pose_grid.addWidget(QLabel("當前角速度:"), 3, 0)
        pose_grid.addWidget(self.lbl_angular_vel, 3, 1)

        pose_grid.addWidget(QLabel("當前角度 (角度):"), 4, 0)
        pose_grid.addWidget(self.lbl_theta_deg, 4, 1)

        pose_grid.addWidget(QLabel("當前角度 (弧度):"), 5, 0)
        pose_grid.addWidget(self.lbl_theta_rad, 5, 1)

        pose_group.setLayout(pose_grid)

        # ------------------ 2. 速度微調區塊 ------------------
        speed_group = QGroupBox("目標速度設定")
        speed_layout = QHBoxLayout()

        self.linear_spin = QDoubleSpinBox()
        self.linear_spin.setRange(0.0, 5.0)
        self.linear_spin.setValue(self.ros_node.target_linear_speed)
        self.linear_spin.setSingleStep(0.2)
        self.linear_spin.valueChanged.connect(self.update_speeds)

        self.angular_spin = QDoubleSpinBox()
        self.angular_spin.setRange(0.0, 5.0)
        self.angular_spin.setValue(self.ros_node.target_angular_speed)
        self.angular_spin.setSingleStep(0.2)
        self.angular_spin.valueChanged.connect(self.update_speeds)

        speed_layout.addWidget(QLabel("線速度:"))
        speed_layout.addWidget(self.linear_spin)
        speed_layout.addWidget(QLabel("角速度:"))
        speed_layout.addWidget(self.angular_spin)
        speed_group.setLayout(speed_layout)

        # ------------------ 3. 方向控制區塊 ------------------
        ctrl_group = QGroupBox("方向控制盤")
        btn_layout = QVBoxLayout()

        btn_up = QPushButton("▲ 前進")
        btn_down = QPushButton("▼ 後退")
        btn_left = QPushButton("◄ 原地左轉")
        btn_right = QPushButton("► 原地右轉")
        btn_stop = QPushButton("█ 停止")
        btn_stop.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")

        btn_up.clicked.connect(self.set_move_forward)
        btn_down.clicked.connect(self.set_move_backward)
        btn_left.clicked.connect(self.set_turn_left)
        btn_right.clicked.connect(self.set_turn_right)
        btn_stop.clicked.connect(self.set_stop)

        btn_layout.addWidget(btn_up, alignment=Qt.AlignCenter)
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(btn_left)
        lr_layout.addWidget(btn_stop)
        lr_layout.addWidget(btn_right)
        btn_layout.addLayout(lr_layout)
        btn_layout.addWidget(btn_down, alignment=Qt.AlignCenter)
        
        ctrl_group.setLayout(btn_layout)

        # ------------------ 主佈局整合 ------------------
        main_layout = QVBoxLayout()
        main_layout.addWidget(pose_group)
        main_layout.addWidget(speed_group)
        main_layout.addWidget(ctrl_group)
        self.setLayout(main_layout)

    def update_pose_ui(self, pose: Pose):
        """當接收到 Pose Signal 時，更新 UI 顯示畫面"""
        self.lbl_x.setText(f"{pose.x:.2f}")
        self.lbl_y.setText(f"{pose.y:.2f}")
        self.lbl_linear_vel.setText(f"{pose.linear_velocity:.2f} m/s")
        self.lbl_angular_vel.setText(f"{pose.angular_velocity:.2f} rad/s")
        
        # 顯示弧度與角度（角度 = 弧度 * 180 / π）
        deg = pose.theta * 180.0 / math.pi
        self.lbl_theta_deg.setText(f"{deg:.2f}°")
        self.lbl_theta_rad.setText(f"{pose.theta:.2f} rad")

    def update_speeds(self):
        self.ros_node.target_linear_speed = self.linear_spin.value()
        self.ros_node.target_angular_speed = self.angular_spin.value()

    def set_move_forward(self):
        self.ros_node.dir_linear = 1

    def set_move_backward(self):
        self.ros_node.dir_linear = -1

    def set_turn_left(self):
        self.ros_node.dir_angular = 1

    def set_turn_right(self):
        self.ros_node.dir_angular = -1

    def set_stop(self):
        self.ros_node.dir_linear = 0
        self.ros_node.dir_angular = 0


def main(args=None):
    rclpy.init(args=args)

    # 1. 建立 Qt Signal 溝通對象與 ROS 2 節點
    comm = Communicate()
    ros_node = TurtleAdvanceCtrlNode(comm)

    # 2. 開啟背景執行緒跑 rclpy.spin
    ros_thread = threading.Thread(target=rclpy.spin, args=(ros_node,), daemon=True)
    ros_thread.start()

    # 3. 啟動 PyQt 介面
    app = QApplication(sys.argv)
    window = TurtleAdvanceWindow(ros_node, comm)
    window.show()

    exit_code = app.exec_()

    # 4. 資源釋放
    ros_node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import sys
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox)
from PyQt5.QtCore import Qt

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleGuiNode(Node):
    """ROS 2 節點：維護速度狀態並透過定時器（10Hz）持續發送指令"""
    def __init__(self):
        super().__init__('turtle_gui_ctrl_node')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # 移動狀態變數 (1 表示前進/左轉, -1 表示後退/右轉, 0 表示停止)
        self.dir_linear = 0
        self.dir_angular = 0
        
        # 設定目標速度大小
        self.target_linear_speed = 2.0
        self.target_angular_speed = 1.5

        # 建立定時器 (0.1 秒發送一次，即 10Hz)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('Turtle GUI Continuous Control Node 已啟動！')

    def timer_callback(self):
        msg = Twist()
        # 計算當前的線速度與角速度（大小 x 方向）
        msg.linear.x = float(self.dir_linear * self.target_linear_speed)
        msg.angular.z = float(self.dir_angular * self.target_angular_speed)
        
        self.publisher_.publish(msg)


class TurtleControlWindow(QWidget):
    """PyQt5 圖形化介面"""
    def __init__(self, ros_node: TurtleGuiNode):
        super().__init__()
        self.ros_node = ros_node
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ROS 2 Turtle GUI 即時同步控制器')
        self.resize(340, 280)

        # 線速度數值微調框
        self.linear_spin = QDoubleSpinBox()
        self.linear_spin.setRange(0.0, 5.0)
        self.linear_spin.setValue(self.ros_node.target_linear_speed)
        self.linear_spin.setSingleStep(0.2)
        # 當數值改變時，即時更新 ROS 節點的速度變數
        self.linear_spin.valueChanged.connect(self.update_speeds)

        # 角速度數值微調框
        self.angular_spin = QDoubleSpinBox()
        self.angular_spin.setRange(0.0, 5.0)
        self.angular_spin.setValue(self.ros_node.target_angular_speed)
        self.angular_spin.setSingleStep(0.2)
        # 當數值改變時，即時更新 ROS 節點的速度變數
        self.angular_spin.valueChanged.connect(self.update_speeds)

        # 速度設定佈局
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("線速度:"))
        speed_layout.addWidget(self.linear_spin)
        speed_layout.addWidget(QLabel("角速度:"))
        speed_layout.addWidget(self.angular_spin)

        # 控制按鈕
        btn_up = QPushButton("▲ 前進")
        btn_down = QPushButton("▼ 後退")
        btn_left = QPushButton("◄ 原地左轉")
        btn_right = QPushButton("► 原地右轉")
        btn_stop = QPushButton("█ 停止")
        btn_stop.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")

        # 按鈕事件綁定 (切換運動狀態)
        btn_up.clicked.connect(self.set_move_forward)
        btn_down.clicked.connect(self.set_move_backward)
        btn_left.clicked.connect(self.set_turn_left)
        btn_right.clicked.connect(self.set_turn_right)
        btn_stop.clicked.connect(self.set_stop)

        # 按鈕佈局
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(btn_up, alignment=Qt.AlignCenter)
        
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(btn_left)
        lr_layout.addWidget(btn_stop)
        lr_layout.addWidget(btn_right)
        btn_layout.addLayout(lr_layout)
        
        btn_layout.addWidget(btn_down, alignment=Qt.AlignCenter)

        # 主佈局
        main_layout = QVBoxLayout()
        main_layout.addLayout(speed_layout)
        main_layout.addSpacing(15)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def update_speeds(self):
        """當 SpinBox 的數值調整時，即時更新 ROS 節點內的速度數值"""
        self.ros_node.target_linear_speed = self.linear_spin.value()
        self.ros_node.target_angular_speed = self.angular_spin.value()

    # 按鈕控制狀態變更
    def set_move_forward(self):
        self.ros_node.dir_linear = 1
        # 若想讓小烏龜在移動時也能同時旋轉（畫圓），這裡不重置 dir_angular
        
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
    ros_node = TurtleGuiNode()

    # 開啟獨立背景執行緒運行 ROS 2 spin
    ros_thread = threading.Thread(target=rclpy.spin, args=(ros_node,), daemon=True)
    ros_thread.start()

    app = QApplication(sys.argv)
    window = TurtleControlWindow(ros_node)
    window.show()

    exit_code = app.exec_()

    ros_node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtleCtrlNode(Node):
    def __init__(self):
        # 1. 初始化節點名稱為 'turtle_ctrl_node'
        super().__init__('turtle_ctrl_node')
        
        # 2. 創建 Publisher
        # 話題名稱: '/turtle1/cmd_vel'
        # 消息型別: Twist
        # Queue size (佇列大小): 10
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # 3. 創建定時器（例如 10 Hz，即每 0.1 秒執行一次控制指令發送）
        timer_period = 0.1  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info('Turtle Control Node 已成功啟動，開始發送速度指令...')

    def timer_callback(self):
        # 4. 建立 Twist 速度指令消息
        msg = Twist()
        
        # 設定線速度（前進速度，單位：m/s）
        msg.linear.x = 2.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        
        # 設定角速度（旋轉速度，單位：rad/s）
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 1.0  # 使小烏龜做圓周運動
        
        # 5. 發送消息
        self.publisher_.publish(msg)

def main(args=None):
    # 初始化 ROS 2 Python 客戶端庫
    rclpy.init(args=args)
    
    # 建立節點實例
    node = TurtleCtrlNode()
    
    try:
        # 保持節點運行，等待並處理事件
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 銷毀節點與關閉 ROS 2
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
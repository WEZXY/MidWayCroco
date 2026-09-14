#!/home/elmoslimany/ros2_ws/src/.venv/bin/python
import rclpy
from rclpy.node import Node
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions

class Robot(Node):
    def __init__(self):
        super().__init__('Control_Unit')
        self.counter=0.0
        self.get_logger().info('Starting Control Unit')
        self.arduino_reading_sub = self.create_subscription(ArduinoActions, 'arduino_writing', self.writing_callback, 10)
        self.cmd_vel_pub = self.create_publisher(ArduinoReading, 'arduino_reading', 10)
        self.create_timer(0.1, self.timer_callback)

    def writing_callback(self, msg):
        pass

    def timer_callback(self):
        pass


def main(args=None):
    rclpy.init(args=args)

    robot = Robot()
    rclpy.spin(robot)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
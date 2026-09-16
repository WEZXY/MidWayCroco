#!/home/elmoslimany/ros2_ws/src/.venv/bin/python
import rclpy
from rclpy.node import Node
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions

class Robot(Node):
    def __init__(self):
        super().__init__('Control_Unit')
        self.counter=0.0
        self.get_logger().info('Starting Control Unit')
        self.arduino_reading_sub = self.create_subscription(ArduinoReading, 'arduino_reading', self.reading_callback, 10)
        self.cmd_vel_pub = self.create_publisher(ArduinoActions, 'arduino_writing', 10)
        self.create_timer(0.1, self.timer_callback)

    def reading_callback(self, msg):
        pass

    def timer_callback(self):
        msg = ArduinoActions()
        msg.window = False
        msg.door = False
        msg.buzzer = False
        msg.light = 0
        msg.fan_speed = 0
        msg.lcd_message = ''
        self.cmd_vel_pub.publish(msg)

    # readings
    def temperature_sensor(self):
        pass

    def humidity_sensor(self):
        pass

    def ir_sensor(self):
        pass

    def light_sensor(self):
        pass

    def pir_sensor(self):
        pass

    def keypad(self):
        pass

    # actions
    def window(self):
        pass

    def door(self):
        pass

    def buzzer(self):
        pass

    def light(self):
        pass

    def fan_speed(self):
        pass

    def lcd_message(self):
        pass



def main(args=None):
    rclpy.init(args=args)

    robot = Robot()
    rclpy.spin(robot)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
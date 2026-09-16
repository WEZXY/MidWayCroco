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
        self.latest_readings = ArduinoReading()
        self.action_msg = ArduinoActions()

    def reading_callback(self, msg):
        self.latest_readings=msg

    def timer_callback(self):
        self.action_msg=ArduinoActions()
        self.light_sensor()
        self.window()
        self.light()
        self.cmd_vel_pub.publish(self.action_msg)
        

    # readings
    def temperature_sensor(self):
        pass

    def humidity_sensor(self):
        pass

    def ir_sensor(self):
        pass

    def light_sensor(self):
        light_val = self.latest_readings.light
        if light_val < 50:
            self.light(1)
            self.window(False)
        else:
            self.light(0)
            self.windoow(True)
    def pir_sensor(self):
        pass

    def keypad(self):
        pass

    # actions
    def window(self, state=True):
        self.action_msg.window = state

    def door(self):
        pass

    def buzzer(self):
        pass

    def light(self, state=1):
        self.action_msg.light = state

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
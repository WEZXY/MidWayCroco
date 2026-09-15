#!/home/elmoslimany/ros2_ws/src/.venv/bin/python
import rclpy
from rclpy.node import Node
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions

class Robot(Node):
    def __init__(self):
        super().__init__('Control_Unit')
        self.counter=0.0
        self.get_logger().info('Starting Control Unit')
        self.arduino_reading_sub = self.create_subscription(
            ArduinoReading, 'arduino_reading', self.reading_callback, 10)
        self.cmd_vel_pub = self.create_publisher(
            ArduinoActions, 'arduino_writing', 10)
        self.create_timer(0.1, self.timer_callback)

        self.ir_value = None
        self.ir_alert = False 

    def reading_callback(self, msg):
        self.ir_value = msg.ir

    def timer_callback(self):
        self.ir_sensor()

        action_msg = ArduinoActions()
        action_msg.buzzer = self.buzzer()




        self.cmd_vel_pub.publish(action_msg)

    # readings
    def temperature_sensor(self):
        pass

    def humidity_sensor(self):
        pass

    def ir_sensor(self):
        if self.ir_value is None:
            return 
        ir_threshold = 150 #n4of el 7war da b3den 
        self.ir_alert = self.ir_value > ir_threshold

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
        return self.ir_alert 

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
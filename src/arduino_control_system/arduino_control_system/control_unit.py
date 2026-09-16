#!/home/elmoslimany/ros2_ws/src/.venv/bin/python
import rclpy
from rclpy.node import Node
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions

class Robot(Node):
    def __init__(self):
        super().__init__('Control_Unit')
        self.counter=0.0

        #------temp & gas sensor reading-------#
        self.temperature = 0
        self.gas = 0
        #--------------------------------------#

        self.get_logger().info('Starting Control Unit')
        self.arduino_reading_sub = self.create_subscription(ArduinoReading, 'arduino_reading', self.reading_callback, 10)
        self.cmd_vel_pub = self.create_publisher(ArduinoActions, 'arduino_writing', 10)
        self.create_timer(0.1, self.timer_callback)

    def reading_callback(self, msg):
        self.temperature = msg.temperature 
        self.gas = msg.gas

    def timer_callback(self):
        actions = ArduinoActions()

        actions.fan_speed = self.fan_speed()
        actions.buzzer = self.buzzer()
        self.cmd_vel_pub.publish(actions)

    # readings
    def temperature_sensor(self):
        return self.temperature

    def gas_sensor(self):
        return self.gas
    
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
        if self.gas_sensor() > 500 :
            return True
        else:
            return False

    def light(self):
        pass

    def fan_speed(self):
        if self.temperature_sensor() > 30 :
            return 255
        else:
            return 0

    def lcd_message(self):
        pass



def main(args=None):
    rclpy.init(args=args)

    robot = Robot()
    rclpy.spin(robot)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
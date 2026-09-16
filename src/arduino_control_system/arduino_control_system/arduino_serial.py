#!/home/elmoslimany/ros2_ws/src/.venv/bin/python

import rclpy
from rclpy.node import Node
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions
import serial


class Robot(Node):

    def __init__(self):
        super().__init__('Arduino_Serial')

        self.get_logger().info('Starting Arduino Serial')

        # Arduino Serial
        self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)

        # Arduino → ROS
        self.reading_pub = self.create_publisher(
            ArduinoReading,
            'arduino_reading',
            10
        )

        # ROS → Arduino
        self.actions_sub = self.create_subscription(
            ArduinoActions,
            'arduino_writing',
            self.writing_callback,
            10
        )

        self.create_timer(0.1, self.timer_callback)

    def writing_callback(self, msg):

        # Fan command
        if msg.fan_speed > 0:
            self.arduino.write(b'FAN_ON\n')
        else:
            self.arduino.write(b'FAN_OFF\n')

        # Buzzer command
        if msg.buzzer:
            self.arduino.write(b'ALARM_ON\n')
        else:
            self.arduino.write(b'ALARM_OFF\n')

    def timer_callback(self):
<<<<<<< HEAD
        msg = ArduinoReading()
        msg.temperature = 0
        msg.humidity = 0
        msg.ir = 0
        msg.light = 0
        msg.keypad = 0
        msg.pir = 0
        self.cmd_vel_pub.publish(msg)

    def read_serial(self):
        pass
=======

        if self.arduino.in_waiting > 0:

            line = self.arduino.readline().decode().strip()

            try:
               
                data = line.split(',')

                temperature = float(data[0].split(':')[1])
                gas = int(data[1].split(':')[1])

                msg = ArduinoReading()

                msg.temperature = int(temperature)
                msg.gas = gas

                self.reading_pub.publish(msg)

            except (ValueError, IndexError):
                pass
>>>>>>> origin/ahmed-control-unit


def main(args=None):

    rclpy.init(args=args)

    robot = Robot()

    rclpy.spin(robot)

    robot.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions
import serial


class ArduinoSerialNode(Node):

    def __init__(self):
        super().__init__('arduino_serial')
        self.get_logger().info('Starting Arduino Serial Node')

        self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)

        self.reading_pub = self.create_publisher(
            ArduinoReading,
            'arduino_reading',
            10
        )

        self.actions_sub = self.create_subscription(
            ArduinoActions,
            'arduino_writing',
            self.writing_callback,
            10
        )

        self.create_timer(0.05, self.timer_callback)

    def writing_callback(self, msg):
        """Sends CSV line: window,door,buzzer,light,fan_speed,lcd_message\n"""
        cmd_str = f"{int(msg.window)},{int(msg.door)},{int(msg.buzzer)},{int(msg.light)},{int(msg.fan_speed)},{msg.lcd_message}\n"
        self.arduino.write(cmd_str.encode('ascii', errors='ignore'))

    def timer_callback(self):
        print("timer callback")
        if True:
            print("in_waiting")
            print(self.arduino.readline().decode('ascii', errors='ignore').strip())
            try:
                print("reading")
                line = self.arduino.readline().decode('ascii', errors='ignore').strip()
                if not line:
                    print("none")
                    return

                data = line.split(',')
                if len(data) == 7:
                    msg = ArduinoReading()
                    msg.temperature = int(data[0])
                    msg.gas         = int(data[1])
                    msg.humidity    = int(data[2])
                    msg.ir          = int(data[3])
                    msg.light       = int(data[4])
                    msg.keypad      = int(data[5])
                    msg.pir         = int(data[6])

                    self.reading_pub.publish(msg)

            except (ValueError, IndexError):
                print("error")


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoSerialNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
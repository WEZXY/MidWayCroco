#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import csv
import os
from datetime import datetime
from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions, GUICommand


class ControlUnitNode(Node):

    def __init__(self):
        super().__init__('control_unit')
        self.get_logger().info('Starting Control Unit with Data Logger')

        self.log_file = "smart_home_logs.csv"
        self.init_csv_file()

        # State Variables
        self.latest_readings = ArduinoReading()
        self.gui_cmd = GUICommand()
        self.has_gui_cmd = False

        self.reading_sub = self.create_subscription(
            ArduinoReading, 'arduino_reading', self.reading_callback, 10
        )
        self.gui_sub = self.create_subscription(
            GUICommand, 'gui_command', self.gui_callback, 10
        )
        self.actions_pub = self.create_publisher(
            ArduinoActions, 'arduino_writing', 10
        )

        self.create_timer(0.01, self.timer_callback)
        self.create_timer(1.0, self.log_to_csv_callback)  # Log to CSV at 1 Hz

    def init_csv_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Date", "Time", "Temp", "Gas", "Humidity", "Light",
                    "IR", "PIR", "Keypad", "Buzzer", "Window", "Door",
                    "Fan", "RoomLight", "LCD Message", "Code"
                ])

    def reading_callback(self, msg):
        self.latest_readings = msg

    def gui_callback(self, msg):
        self.gui_cmd = msg
        self.has_gui_cmd = True

    def timer_callback(self):
        action = ArduinoActions()

        # 1. Automatic Sensor Safety Logic
        gas_alert = self.latest_readings.gas > 500
        ir_alert = self.latest_readings.ir > 400
        auto_buzzer = gas_alert or ir_alert

        auto_light = self.latest_readings.light > 400
        auto_window = not auto_light
        auto_fan = 255 if self.latest_readings.temperature > 30 else 0

        # 2. Merge Auto Logic with GUI Manual Overrides
        if self.has_gui_cmd:
            action.window = self.gui_cmd.window
            action.door = self.gui_cmd.door
            action.light = self.gui_cmd.light
            action.fan_speed = self.gui_cmd.fan_speed
            action.lcd_message = self.gui_cmd.lcd_message
        else:
            action.window = auto_window
            action.door = False
            action.light = auto_light
            action.fan_speed = auto_fan
            action.lcd_message = "System OK"

        action.buzzer = auto_buzzer or (self.gui_cmd.buzzer if hasattr(self.gui_cmd, 'buzzer') else False)
        self.current_action = action
        self.actions_pub.publish(action)

    def log_to_csv_callback(self):
        if not hasattr(self, 'current_action'):
            return

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        code = "OK"
        if self.latest_readings.gas > 500:
            code = "GAS_ALERT"
        elif self.latest_readings.ir > 400:
            code = "IR_ALERT"

        row = [
            date_str,
            time_str,
            self.latest_readings.temperature,
            self.latest_readings.gas,
            self.latest_readings.humidity,
            self.latest_readings.light,
            self.latest_readings.ir,
            self.latest_readings.pir,
            self.latest_readings.keypad,
            1 if self.current_action.buzzer else 0,
            1 if self.current_action.window else 0,
            1 if self.current_action.door else 0,
            self.current_action.fan_speed,
            1 if self.current_action.light else 0,
            self.current_action.lcd_message,
            code
        ]

        with open(self.log_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)


def main(args=None):
    rclpy.init(args=args)
    node = ControlUnitNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
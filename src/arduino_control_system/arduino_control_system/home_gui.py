#!/usr/bin/env python3
import sys
import csv
import os
from datetime import datetime, timedelta

import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QDate, QTime, QThread, pyqtSignal, pyqtSlot

from custom_msg_interfaces.msg import ArduinoReading, ArduinoActions, GUICommand

from ament_index_python.packages import get_package_share_directory
import os


# -------------------------------------------------------------
# 1. ROS 2 Worker Running in a Dedicated QThread
# -------------------------------------------------------------
class Ros2Worker(QThread):
    # Signals to pass ROS messages safely to the Main UI Thread
    reading_received = pyqtSignal(ArduinoReading)
    actions_received = pyqtSignal(ArduinoActions)

    def __init__(self):
        super().__init__()
        self.node = None
        self.gui_pub = None

    def run(self):
        # Initialize Node inside the dedicated thread context
        self.node = Node('home_gui_worker')
        self.gui_pub = self.node.create_publisher(GUICommand, 'gui_command', 10)

        self.node.create_subscription(
            ArduinoReading, 'arduino_reading', self._on_reading, 10
        )
        self.node.create_subscription(
            ArduinoActions, 'arduino_writing', self._on_actions, 10
        )

        # Spin ROS 2 event loop safely off the main UI thread
        rclpy.spin(self.node)

    def _on_reading(self, msg):
        self.reading_received.emit(msg)

    def _on_actions(self, msg):
        self.actions_received.emit(msg)

    def publish_gui_cmd(self, cmd):
        if self.gui_pub and self.node:
            self.gui_pub.publish(cmd)

    def stop(self):
        if self.node:
            self.node.destroy_node()
        self.quit()
        self.wait()


# -------------------------------------------------------------
# 2. CSV File Loader Thread (Prevents UI Lag on Disk I/O)
# -------------------------------------------------------------
class LogLoaderThread(QThread):
    logs_loaded = pyqtSignal(list)

    def __init__(self, start_dt, end_dt, file_path="smart_home_logs.csv"):
        super().__init__()
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.file_path = file_path

    def run(self):
        rows_to_insert = []
        try:
            with open(self.file_path, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip Header

                for row in reader:
                    if len(row) < 16:
                        continue

                    row_dt = datetime.strptime(f"{row[0]} {row[1]}", "%Y-%m-%d %H:%M:%S")

                    if self.start_dt <= row_dt < self.end_dt:
                        rows_to_insert.append(row)
                        if len(rows_to_insert) >= 3600:
                            break
                    elif row_dt >= self.end_dt:
                        break
        except FileNotFoundError:
            pass

        self.logs_loaded.emit(rows_to_insert)


# -------------------------------------------------------------
# 3. Main GUI Window
# -------------------------------------------------------------
class HomeGuiWindow(QMainWindow):

    def __init__(self, ui_file_path):
        super().__init__()

        # Load UI directly into this QMainWindow instance
        uic.loadUi(ui_file_path, self)

        # Start ROS 2 Worker Thread
        self.ros_thread = Ros2Worker()
        self.ros_thread.reading_received.connect(self.update_sensor_readings)
        self.ros_thread.actions_received.connect(self.update_action_status)
        self.ros_thread.start()

        # UI Table Configuration
        self.tableLogs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        now = datetime.now()
        self.datePicker.setDate(QDate(now.year, now.month, now.day))
        self.timePicker.setTime(QTime(now.hour, now.minute, now.second))

        # Setup Button Controls
        self.btnWindow.clicked.connect(lambda chk: self.on_btn_toggled(self.btnWindow, "Window (Servo)", chk))
        self.btnDoor.clicked.connect(lambda chk: self.on_btn_toggled(self.btnDoor, "Door (LED)", chk))
        self.btnLight.clicked.connect(lambda chk: self.on_btn_toggled(self.btnLight, "Room Light", chk))

        self.sliderFan.valueChanged.connect(self.on_fan_slider_changed)
        self.btnSendLcd.clicked.connect(self.send_gui_command)

        self.btnFilterLogs.clicked.connect(self.filter_one_hour_logs)
        self.btnLoadLastHour.clicked.connect(self.load_last_hour_logs)

        self.loader_thread = None

    def on_btn_toggled(self, btn, label, checked):
        btn.setText(f"{label}: {'ON' if checked else 'OFF'}")
        self.send_gui_command()

    def on_fan_slider_changed(self, value):
        self.lblFanSpeed.setText(f"Fan Speed (PWM): {value}")
        self.send_gui_command()

    def send_gui_command(self):
        cmd = GUICommand()
        cmd.window = self.btnWindow.isChecked()
        cmd.door = self.btnDoor.isChecked()
        cmd.light = self.btnLight.isChecked()
        cmd.fan_speed = self.sliderFan.value()
        cmd.lcd_message = self.txtLcdMessage.text()

        self.ros_thread.publish_gui_cmd(cmd)

    @pyqtSlot(ArduinoReading)
    def update_sensor_readings(self, msg):
        self.lblTemp.setText(f"{msg.temperature} °C")
        self.lblGas.setText(f"{msg.gas} PPM")
        self.lblHumidity.setText(f"{msg.humidity} %")
        self.lblLight.setText(f"{msg.light} Lux")
        self.lblIR.setText(str(msg.ir))
        self.lblPIR.setText("N/A")

        key_str = str(msg.keypad) if msg.keypad != -1 else "None"
        self.lblKeypad.setText(key_str)

    @pyqtSlot(ArduinoActions)
    def update_action_status(self, msg):
        self.lblBuzzer.setText("ON" if msg.buzzer else "OFF")

    def filter_one_hour_logs(self):
        target_date_str = self.datePicker.date().toString("yyyy-MM-dd")
        target_time_str = self.timePicker.time().toString("HH:mm:ss")

        start_dt = datetime.strptime(f"{target_date_str} {target_time_str}", "%Y-%m-%d %H:%M:%S")
        end_dt = start_dt + timedelta(hours=1)

        self.start_background_log_loading(start_dt, end_dt)

    def load_last_hour_logs(self):
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(hours=1)
        self.start_background_log_loading(start_dt, end_dt)

    def start_background_log_loading(self, start_dt, end_dt):
        self.btnFilterLogs.setEnabled(False)
        self.btnLoadLastHour.setEnabled(False)
        self.btnFilterLogs.setText("Scanning CSV...")

        self.loader_thread = LogLoaderThread(start_dt, end_dt)
        self.loader_thread.logs_loaded.connect(self.on_logs_loaded)
        self.loader_thread.start()

    def on_logs_loaded(self, rows):
        table = self.tableLogs
        table.setUpdatesEnabled(False)
        table.setRowCount(0)

        table.setRowCount(len(rows))
        for row_idx, data_row in enumerate(rows):
            for col_idx, item_val in enumerate(data_row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(item_val)))

        table.setUpdatesEnabled(True)

        self.btnFilterLogs.setEnabled(True)
        self.btnLoadLastHour.setEnabled(True)
        self.btnFilterLogs.setText("Filter 1-Hour Window")

    def closeEvent(self, event):
        # Stop background ROS thread on window exit
        self.ros_thread.stop()
        event.accept()


def main(args=None):
    # 1. Main Qt Application
    app = QApplication(sys.argv)

    # 2. Init ROS 2 Context
    rclpy.init(args=args)

    # 3. Resolve absolute UI path
    try:
        pkg_share = get_package_share_directory('arduino_control_system')
        ui_file_path = os.path.join(pkg_share, 'smart_home_system.ui')
    except Exception:
        ui_file_path = os.path.join(os.path.dirname(__file__), 'smart_home_system.ui')

    if not os.path.exists(ui_file_path):
        ui_file_path = 'smart_home_system.ui'

    # 4. Display Window
    gui_window = HomeGuiWindow(ui_file_path)
    gui_window.show()

    exit_code = app.exec_()

    # Clean shutdown
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
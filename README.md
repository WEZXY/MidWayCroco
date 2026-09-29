# Smart Home ROS 2 & Arduino Control System

A complete real-time Smart Home automation and telemetry pipeline integrating an **Arduino Uno**, a **ROS 2** Python backend, and a multithreaded **PyQt5** graphical user interface. The system reads environmental sensors, parses keypad inputs, logs data to CSV, and drives actuators based on threshold rules or manual GUI overrides.

---

## 🏛️ System Architecture

```
[ Arduino Uno ] <--- (Serial CSV @ 9600 Baud) ---> [ arduino_serial.py ]
  (Sensors/Actuators)                                     |
                                                     (ROS 2 Topics)
                                                          |
                                           +--------------+--------------+
                                           |                             |
                                  [ control_unit.py ]           [ home_gui.py ]
                              (CSV Logger & Rules)        (PyQt5 Dashboard)
```

1. **Arduino Firmware (`smart_home_arduino.ino`):** Reads analog/digital sensors and matrix keypad, writes formatted CSV lines to Serial every cycle, reads incoming serial actuation strings, and drives outputs.
2. **Serial Translation Node (`arduino_serial.py`):** Bridges `/dev/ttyACM0` and ROS 2 by converting raw ASCII serial lines into custom ROS messages (`ArduinoReading.msg`) and publishing execution commands back over serial (`ArduinoActions.msg`).
3. **Control & Logging Node (`control_unit.py`):** Implements threshold-based automation rules and writes historical telemetry records to `smart_home_logs.csv`.
4. **GUI Dashboard (`home_gui.py`):** A dark-mode PyQt5 interface running ROS 2 spinning in an isolated worker thread (`Ros2Worker` / `QThread`) to allow zero-latency UI updates, live telemetry visualization, and PWM fan speed control.

---

## 📌 Hardware Pinout Map

| Component | Signal / Pin Name | Arduino Pin | Mode / Function |
|---|---|---|---|
| **Window Servo Motor** | `SERVO_PIN` | **Digital 3** | PWM Output (0° / 90°) |
| **DHT11 Temp/Humidity** | `DHT_PIN` | **Digital 4** | One-Wire Digital Input |
| **DC Fan Speed Control** | `FAN_PWM_PIN` | **Digital 5** | PWM Analog Output (0–255) |
| **Alarm Buzzer** | `BUZZER_PIN` | **Digital 6** | Digital Output |
| **Room Light LED** | `LIGHT_LED_PIN` | **Digital 7** | Digital Output |
| **Door Indicator LED** | `DOOR_LED_PIN` | **Analog A3** | Digital Output |
| **Light Sensor (LDR)** | `LIGHT_PIN` | **Analog A0** | Analog Read |
| **IR Proximity Sensor** | `IR_PIN` | **Analog A1** | Analog Read |
| **MQ Gas Sensor** | `GAS_PIN` | **Analog A2** | Analog Read |
| **4x3 Keypad Rows** | `ROW_PINS` | **Digital 10, 11, 12, 13** | Input with `INPUT_PULLUP` |
| **4x3 Keypad Columns** | `COL_PINS` | **Digital 2, 8, 9** | Digital Output |
| **I2C LCD Display** | `SDA / SCL` | **Analog A4 / A5** | I2C Bus (`0x27` or `0x3F`) |

---

## 📁 Repository Structure

```text
arduino_control_system/
├── arduino_control_system/         # Python ROS 2 Nodes
│   ├── __init__.py
│   ├── arduino_serial.py           # Serial <-> ROS 2 Bridge
│   ├── control_unit.py             # CSV Logger & Automation Logic
│   └── home_gui.py                 # PyQt5 Multithreaded GUI Node
├── msg/                            # Custom ROS 2 Interfaces
│   ├── ArduinoReading.msg          # Telemetry payload definition
│   ├── ArduinoActions.msg          # Actuator command definition
│   └── GUICommand.msg              # GUI interaction payload
├── resource/
│   └── arduino_control_system
├── firmware/
│   └── smart_home_arduino.ino      # Microcontroller Firmware
├── smart_home_system.ui            # Qt Designer UI Layout
├── package.xml
└── setup.py                        # Package build configuration
```

---

## ⚡ Requirements & Dependencies

### Linux Dependencies
* ROS 2 (Humble / Iron / Rolling)
* Python 3.8+
* PyQt5: `pip install PyQt5`
* pySerial: `pip install pyserial`

### Arduino IDE Libraries
* `LiquidCrystal_I2C`
* `DHT sensor library`
* `Servo`

---

## 🚀 Installation & Setup

### 1. Hardware Firmware Flash
1. Open `firmware/smart_home_arduino.ino` in the Arduino IDE.
2. Select **Arduino Uno** and your corresponding port (e.g., `/dev/ttyACM0`).
3. Build and upload the sketch.

### 2. Workspace Build
Clone the package into your ROS 2 workspace `src` directory and build using `colcon`:

```bash
cd ~/ros2_ws/src
# (Ensure arduino_control_system is in this directory)

cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

---

## 🖥️ Execution

Run each node in separate terminal windows (ensure workspace is sourced in each):

1. **Launch Serial Bridge Node:**
   ```bash
   ros2 run arduino_control_system arduino_serial
   ```

2. **Launch Control Unit & CSV Logger:**
   ```bash
   ros2 run arduino_control_system control_unit
   ```

3. **Launch Graphical Interface:**
   ```bash
   ros2 run arduino_control_system home_gui
   ```

---

## 🔧 Troubleshooting

* **Serial Port Access (`Permission Denied`):**
  Add your Linux user to the `dialout` group to access serial ports without `sudo`:
  ```bash
  sudo usermod -aG dialout $USER
  ```
  *(Log out and back in for changes to take effect.)*

* **Port Busy (`Device or resource busy`):**
  Kill any lingering process holding `/dev/ttyACM0`:
  ```bash
  sudo fuser -k /dev/ttyACM0
  ```

* **LCD Screen Locks MCU on Boot:**
  If the LCD address is `0x3F` instead of `0x27`, `lcd.init()` will freeze execution. Verify the module address using an I2C scanner sketch or update the address parameter in `smart_home_arduino.ino`:
  ```cpp
  LiquidCrystal_I2C lcd(0x3F, 16, 2);
  ```

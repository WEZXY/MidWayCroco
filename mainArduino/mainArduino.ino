#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// ==========================================
// CONFIGURATION & CONSTANTS
// ==========================================

// Servo Angle Settings
const int WINDOW_OPEN_ANGLE  = 90;
const int WINDOW_CLOSED_ANGLE = 0;

// Fan Threshold (0-255 PWM input range)
const int FAN_THRESHOLD = 128;

// Actuator Pins
const int SERVO_PIN     = 3;   // Window Servo Motor
const int FAN_PWM_PIN   = 4;   // DC Fan Speed Control (Active LOW)
const int DOOR_LED_PIN  = 5;   // Door Indicator LED
const int BUZZER_PIN    = 6;   // Alarm Buzzer
const int LIGHT_LED_PIN = 7;   // Room Light LED

// Analog Sensor Pins
const int IR_PIN        = A0;  // IR Proximity Sensor
const int GAS_PIN       = A1;  // MQ Gas Sensor
const int LIGHT_PIN     = A2;  // LDR Light Sensor

// Digital Sensor Pins
const int DHT_PIN       = A3;  // DHT11 Temp/Humidity Sensor

// Matrix Keypad Config
const byte ROWS = 4;
const byte COLS = 3;

const char KEYPAD_MAP[ROWS][COLS] = {
  {'1', '2', '3'},
  {'4', '5', '6'},
  {'7', '8', '9'},
  {'*', '0', '#'}
};

const byte ROW_PINS[ROWS] = {13, 12, 11, 10};
const byte COL_PINS[COLS] = {9, 8, 2};

// ==========================================
// PERIPHERAL OBJECTS
// ==========================================

DHT dht(DHT_PIN, DHT11);
LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo windowServo;

// ==========================================
// HELPER FUNCTIONS
// ==========================================

// Scans the 4x3 matrix keypad for an active key press
char readKeypad() {
  for (byte c = 0; c < COLS; c++) {
    digitalWrite(COL_PINS[c], LOW);

    for (byte r = 0; r < ROWS; r++) {
      if (digitalRead(ROW_PINS[r]) == LOW) {
        digitalWrite(COL_PINS[c], HIGH);
        return KEYPAD_MAP[r][c];
      }
    }
    digitalWrite(COL_PINS[c], HIGH);
  }
  return 0; // No key pressed
}

// Converts key characters into numeric codes for ROS 2 (-1 = None)
int16_t parseKeypadValue(char key) {
  if (key >= '0' && key <= '9') {
    return key - '0';
  } else if (key != 0) {
    return (int16_t)key;
  } else {
    return -1;
  }
}

// Transmits CSV telemetry line over Serial: "TEMP,GAS,HUM,IR,LIGHT,KEYPAD,PIR"
void transmitTelemetry(int temp, int gas, int hum, int ir, int light, int16_t keyVal) {
  Serial.print(temp);   Serial.print(",");
  Serial.print(gas);    Serial.print(",");
  Serial.print(hum);    Serial.print(",");
  Serial.print(ir);     Serial.print(",");
  Serial.print(light);  Serial.print(",");
  Serial.print(keyVal); Serial.print(",");
  Serial.println(0);    // PIR dummy value
}

// Parses incoming serial commands: "WINDOW,DOOR,BUZZER,LIGHT,FAN_SPEED,LCD_MSG"
void processIncomingCommands() {
  if (Serial.available() <= 0) {
    return;
  }

  int winCmd   = Serial.parseInt();
  int doorCmd  = Serial.parseInt();
  int buzzCmd  = Serial.parseInt();
  int lightCmd = Serial.parseInt();
  int fanCmd   = Serial.parseInt();

  String lcdMsg = Serial.readStringUntil('\n');
  lcdMsg.trim();
  if (lcdMsg.startsWith(",")) {
    lcdMsg = lcdMsg.substring(1);
  }

  // --- 1. Actuate Window Servo ---
  if (winCmd > 0) {
    windowServo.write(WINDOW_OPEN_ANGLE);
  } else {
    windowServo.write(WINDOW_CLOSED_ANGLE);
  }

  // --- 2. Actuate Door LED ---
  if (doorCmd > 0) {
    digitalWrite(DOOR_LED_PIN, HIGH);
  } else {
    digitalWrite(DOOR_LED_PIN, LOW);
  }

  // --- 3. Actuate Buzzer ---
  if (buzzCmd > 0) {
    tone(BUZZER_PIN, 1000); // Plays a 1000 Hz tone
  } else {
    noTone(BUZZER_PIN);      // Silences the buzzer
  }

  // --- 4. Actuate Light LED ---
  if (lightCmd > 0) {
    digitalWrite(LIGHT_LED_PIN, HIGH);
  } else {
    digitalWrite(LIGHT_LED_PIN, LOW);
  }

  // --- 5. Actuate Fan (Active LOW Logic: LOW turns fan ON) ---
  if (fanCmd > FAN_THRESHOLD) {
    digitalWrite(FAN_PWM_PIN, LOW);   // Fan ON
  } else {
    digitalWrite(FAN_PWM_PIN, HIGH);  // Fan OFF
  }

  // --- 6. Update Display ---
  if (lcdMsg.length() > 0) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(lcdMsg.substring(0, 16));
  }
}

// ==========================================
// SETUP & MAIN EXECUTION LOOP
// ==========================================

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100); // Prevents serial buffer stalls

  // Hardware Peripherals Init
  dht.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Smart Home Ready");

  // Actuators Init
  windowServo.attach(SERVO_PIN);
  windowServo.write(WINDOW_CLOSED_ANGLE);

  pinMode(FAN_PWM_PIN, OUTPUT);
  pinMode(DOOR_LED_PIN, OUTPUT);
  pinMode(LIGHT_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(FAN_PWM_PIN, HIGH); // Default Fan OFF (active LOW)
  digitalWrite(DOOR_LED_PIN, LOW);
  digitalWrite(LIGHT_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Keypad Pins Init
  for (byte r = 0; r < ROWS; r++) {
    pinMode(ROW_PINS[r], INPUT_PULLUP);
  }
  for (byte c = 0; c < COLS; c++) {
    pinMode(COL_PINS[c], OUTPUT);
    digitalWrite(COL_PINS[c], HIGH);
  }
}

void loop() {
  // 1. Read Sensors
  int temp       = (int)dht.readTemperature();
  int hum        = (int)dht.readHumidity();
  int gas        = analogRead(GAS_PIN);
  int ir         = analogRead(IR_PIN);
  int light      = analogRead(LIGHT_PIN);
  int16_t keyVal = parseKeypadValue(readKeypad());

  // 2. Write Serial Telemetry
  transmitTelemetry(temp, gas, hum, ir, light, keyVal);

  // 3. Process ROS 2 Response & Actuate
  processIncomingCommands();

  // 4. Cycle Delay
  delay(50);
}

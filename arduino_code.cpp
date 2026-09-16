#define TEMP_PIN A0
#define GAS_PIN  A4

#define FAN_PIN 5
#define BUZZER_PIN 7

void setup() {
  Serial.begin(9600);

  pinMode(FAN_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(FAN_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
}

void loop() {

  // ===== Read Temperature =====
  int tempRaw = analogRead(TEMP_PIN);

  float voltage = tempRaw * (5.0 / 1023.0);

  float temperature = (voltage - 0.5) * 100.0;

  // ===== Read Gas =====
  int gasRaw = analogRead(GAS_PIN);

  // ===== Send sensor data =====
  Serial.print("T:");
  Serial.print(temperature);
  Serial.print(",G:");
  Serial.println(gasRaw);

  // ===== Receive commands =====
  if (Serial.available() > 0) {

    String command = Serial.readStringUntil('\n');

    command.trim();

    if (command == "FAN_ON") {
      digitalWrite(FAN_PIN, HIGH);
    }

    else if (command == "FAN_OFF") {
      digitalWrite(FAN_PIN, LOW);
    }

    else if (command == "ALARM_ON") {
      digitalWrite(BUZZER_PIN, HIGH);
    }

    else if (command == "ALARM_OFF") {
      digitalWrite(BUZZER_PIN, LOW);
    }
  }

  delay(500);
}
#include <Servo.h>

Servo myServo;
const int ledPin = 8;
const int servoPin = 9;
const int ldrPin = A0;

void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);
  pinMode(ledPin, OUTPUT);
  myServo.write(0);
  digitalWrite(ledPin, LOW);
}

void loop() {
  int lightValue = analogRead(ldrPin);
  Serial.print("LIGHT:");
  Serial.println(lightValue);

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("SERVO:")) {
      int angle = command.substring(6).toInt();
      myServo.write(angle);
    } 
    else if (command.startsWith("LED:")) {
      int state = command.substring(4).toInt();
      digitalWrite(ledPin, state);
    }
  }

  delay(200);
}
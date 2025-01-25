#include <Servo.h>

// Define the servo pin and create a servo object
const int servoPin = 9;
Servo doorServo;

// Set the positions for open and close (you can adjust these angles)
int openAngle = 90;  // Angle when the door is open
int closeAngle = 0;  // Angle when the door is closed

// Define the serial message for open and close status
String openMessage = "OPEN";
String closeMessage = "CLOSED";

// Variable to store the servo position
int servoPosition = closeAngle;

void setup() {
  // Start the serial communication
  Serial.begin(9600);

  // Attach the servo to the defined pin
  doorServo.attach(servoPin);

  // Initialize the servo in the closed position
  doorServo.write(closeAngle);
  Serial.println("Door is closed.");
}

void loop() {
  // Listen for incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readString();

    // Check if the received command is "OPEN"
    if (command == openMessage) {
      openDoor();
    }
  }
}

void openDoor() {
  // Move the servo to the open position
  doorServo.write(openAngle);
  servoPosition = openAngle;
  Serial.println("Door opened.");

  // Wait for 5 seconds before closing the door
  delay(5000);

  // Close the door
  closeDoor();
}

void closeDoor() {
  // Move the servo to the closed position
  doorServo.write(closeAngle);
  servoPosition = closeAngle;
  Serial.println("Door closed.");

  // Notify Python to restart face recognition
  Serial.println("RESTART_FACE_RECOGNITION");
}
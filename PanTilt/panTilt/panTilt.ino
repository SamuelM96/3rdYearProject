#include <AccelStepper.h>
#include <MultiStepper.h>
#include <SPI.h>
#include <Wire.h>

// All the wires needed for full functionality
#define PAN_DIR 5
#define PAN_STEP 2
#define TILT_DIR 6
#define TILT_STEP 3
//#define MAX_PAN 4
//#define MAX_TILT 3

AccelStepper pan(AccelStepper::DRIVER, PAN_STEP, PAN_DIR, 0, 0, true);
AccelStepper tilt(AccelStepper::DRIVER, TILT_STEP, TILT_DIR, 0, 0, true);
MultiStepper panTilt;

long panPos = 0;
long tiltPos = 0;
bool manualMode = false;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);

/*
  pan.setMaxSpeed(100);
  tilt.setMaxSpeed(100);
  tilt.setSpeed(100);
  pan.setSpeed(100);
  tilt.setAcceleration(100);
  pan.setAcceleration(100);
*/
    pan.setMaxSpeed(80);
    tilt.setMaxSpeed(80);

    panTilt.addStepper(pan);
    panTilt.addStepper(tilt);

  pinMode(8, OUTPUT);
  digitalWrite(8, LOW);
}

void loop() {
  // Check for commands and read them into a buffer if available
  if (Serial.available()) {
    static char inputBuf[20];
    memset(inputBuf, 0, sizeof(inputBuf));
    int count = Serial.readBytesUntil('\0', inputBuf, sizeof(inputBuf));
    String inputStr(inputBuf);

    // Check which command was given
    if (inputStr.startsWith("PT ")) {
      // Find step count using the format: PTAxB
      // where A and B are the step counts for pan and tilt, respectively.
      String panAndTilt = inputStr.substring(2);
      int separator = panAndTilt.indexOf('x');

      panPos = pan.currentPosition() + panAndTilt.substring(0, separator).toInt();
      tiltPos = tilt.currentPosition() + panAndTilt.substring(separator + 1).toInt();
    } else if (inputStr.startsWith("PAN ")) {
      // Find step count for pan
      int num = inputStr.substring(3).toInt();
      panPos = pan.currentPosition() + num;
    } else if (inputStr.startsWith("TILT ")) {
      // Find step count for tilt
      int num = inputStr.substring(4).toInt();
      tiltPos = tilt.currentPosition() + num;
    } else if (inputStr.startsWith("PAN_SPEED ")) {
        int num = inputStr.substring(9).toInt();
        pan.setMaxSpeed(num);
    } else if (inputStr.startsWith("TILT_SPEED ")) {
        int num = inputStr.substring(10).toInt();
        tilt.setMaxSpeed(num);
    } else if (inputStr.startsWith("SET_PAN ")) {
      int num = inputStr.substring(7).toInt();
      panPos = num;
    } else if (inputStr.startsWith("SET_TILT")) {
      int num = inputStr.substring(8).toInt();
      tiltPos = num;
    } else if (inputStr.startsWith("RESET")) {
      // Reset pan and tilt back to home
      panPos = 0;
      tiltPos = 0;
    } else if (inputStr.startsWith("RESET_PAN")) {
      panPos = 0;
    } else if (inputStr.startsWith("RESET_TILT")) {
      tiltPos = 0;
    } else if (inputStr.startsWith("MANUAL")) {
      manualMode = true;
    } else if (inputStr.startsWith("AUTO")) {
      manualMode = false;
    } else {
      Serial.println("INVALID COMMAND");
    }

    long positions[2];
    positions[0] = panPos;
    positions[1] = tiltPos;
    panTilt.moveTo(positions);
    Serial.print("Pan: ");
    Serial.println(panPos);
    Serial.print("Tilt: ");
    Serial.println(tiltPos);
  }

  if (manualMode) {
    // Block until at position
    panTilt.runSpeedToPosition();
  } else {
    // Iteratively move to new position
    panTilt.run();
  }
}

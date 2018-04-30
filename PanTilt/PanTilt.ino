#include <AccelStepper.h>
#include <MultiStepper.h>
#include <SPI.h>
#include <Wire.h>

// All the wires needed for full functionality
#define PAN_DIR 5
#define PAN_STEP 2
#define TILT_DIR 6
#define TILT_STEP 3
#define TILT_ENDSTOP 10
#define MAX_PAN 235
#define MIN_PAN -MAX_PAN
#define MAX_TILT 900
#define MIN_TILT -310

AccelStepper pan(AccelStepper::DRIVER, PAN_STEP, PAN_DIR, 0, 0, true);
AccelStepper tilt(AccelStepper::DRIVER, TILT_STEP, TILT_DIR, 0, 0, true);
MultiStepper panTilt;

long panPos = 0;
long tiltPos = 0;
int endstopState = LOW;
long tiltComp = 0;

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(50);

    panTilt.addStepper(pan);
    panTilt.addStepper(tilt);

    // Enable motors
    pinMode(8, OUTPUT);
    digitalWrite(8, LOW);

    // Enable endstop
    pinMode(TILT_ENDSTOP, INPUT);
    digitalWrite(TILT_ENDSTOP, HIGH);
    
    // Find endstop
    tilt.setMaxSpeed(200);
    tilt.setSpeed(200);
    while (digitalRead(TILT_ENDSTOP) == LOW) {
        tiltPos -= 1;
        tilt.moveTo(tiltPos);
        tilt.runSpeed();
    }
    
    tilt.stop();
    tiltComp = tilt.currentPosition() - MIN_TILT;
    tiltPos = tiltComp;
    tilt.moveTo(tiltPos);
    tilt.runSpeedToPosition();
    
    pan.setMaxSpeed(120);
    tilt.setMaxSpeed(500);
}

void loop() {
    // Get endstop state
    int endstopState = digitalRead(TILT_ENDSTOP);

    // Check for commands and read them into a buffer if available
    if (Serial.available()) {
        static char inputBuf[20];
        memset(inputBuf, 0, sizeof(inputBuf));
        int count = Serial.readBytesUntil('\0', inputBuf, sizeof(inputBuf));
        String inputStr(inputBuf);
        int tiltMov = 0;
        int panMov = 0;

        // Check which command was given
        if (inputStr.startsWith("PT ")) {
            // Find step count using the format: PTAxB
            // where A and B are the step counts for pan and tilt, respectively.
            String panAndTilt = inputStr.substring(2);
            int separator = panAndTilt.indexOf('x');

            panMov = panAndTilt.substring(0, separator).toInt();
            tiltMov = panAndTilt.substring(separator + 1).toInt();
        } else if (inputStr.startsWith("PAN ")) {
            // Find step count for pan
            panMov = inputStr.substring(3).toInt();
        } else if (inputStr.startsWith("TILT ")) {
            // Find step count for tilt
            tiltMov = inputStr.substring(4).toInt();
        } else if (inputStr.startsWith("PAN_SPEED ")) {
            int speed = inputStr.substring(9).toInt();
            pan.setMaxSpeed(speed);
        } else if (inputStr.startsWith("TILT_SPEED ")) {
            int speed = inputStr.substring(10).toInt();
            tilt.setMaxSpeed(speed);
        } else if (inputStr.startsWith("SET_PAN ")) {
            int newPos = inputStr.substring(7).toInt();
            panMov = newPos - panPos;
        } else if (inputStr.startsWith("SET_TILT")) {
            int newPos = inputStr.substring(8).toInt();
            tiltMov = newPos - tiltPos;
        } else if (inputStr.startsWith("ZERO")) {
            // Reset pan and tilt back to home
            panPos = 0;
            tiltPos = tiltComp;
        } else if (inputStr.startsWith("ZERO_PAN")) {
            panPos = 0;
        } else if (inputStr.startsWith("ZERO_TILT")) {
            tiltPos = tiltComp;
        } else {
            Serial.println("INVALID COMMAND");
        }

        // Prevent tilting from going out of bounds
        long newTiltPos = tiltPos + tiltMov;
        if (newTiltPos < MIN_TILT) {
            tiltPos = MIN_TILT;
        } else if (newTiltPos > MAX_TILT) {
            tiltPos = MAX_TILT;
        } else if (endstopState == LOW || tiltMov > 0) {
            // Only allow upward movement if endstop is triggered
            tiltPos = newTiltPos;
        }

        // Prevent panning from going out of bounds
        long newPanPos = panPos + panMov;
        if (newPanPos > MAX_PAN) {
            panPos = MAX_PAN;
        } else if (newPanPos < MIN_PAN) {
            panPos = MIN_PAN;
        } else {
            panPos = newPanPos;
        }

        long positions[2];
        positions[0] = panPos;
        positions[1] = tiltPos + tiltComp;
        panTilt.moveTo(positions);
        Serial.print("Pan: ");
        Serial.println(panPos);
        Serial.print("Tilt: ");
        Serial.println(tiltPos);
    }

    // Iteratively move to new position
    panTilt.run();
}

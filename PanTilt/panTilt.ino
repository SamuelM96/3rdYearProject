#include <AccelStepper.h>
#include <SPI.h>
#include <Wire.h>

#define MOTOR_STEPS 200

// All the wires needed for full functionality
#define PAN_DIR 5
#define PAN_STEP 2
#define TILT_DIR 6
#define TILT_STEP 3
#define MAX_PAN 4
#define MAX_TILT 3

static const int commandsLen = sizeof(commands)/sizeof(commands[0]);

AccelStepper pan(AccelStepper::DRIVER, PAN_STEP, PAN_DIR, 0, 0, true);
AccelStepper tilt(AccelStepper::DRIVER, TILT_STEP, TILT_DIR, 0, 0, true);
MultiStepper panTilt();

int pan = 0;
int tilt = 0;

void setup() {
    Serial.begin(115200);

    pan.setMaxSpeed(1000);
    tilt.setMaxSpeed(1000);

    panTilt.addStepper(&pan);
    panTilt.addStepper(&tilt);
}

void loop() {
    // Check for commands and read them into a buffer if available
    if(Serial.available()) {
        static char inputBuf[20];
        int count = Serial.readBytesUntil('\0', inputBuf, sizeof(inputBuf));
        String inputStr(inputBuf);

        // Check which command was given
        if (input.startsWith("PT")) {
            // Find step count using the format: PTAxB
            // where A and B are the step counts for pan and tilt, respectively.
            String panAndTilt = inputStr.substring(2);
            int separator = panAndTilt.indexOf('x');
            
            static long nums[2];
            // Pan
            nums[0] = panAndTilt.substring(0, separator).toInt();
            // Tilt
            nums[1] = panAndTilt.substring(separator+1).toInt();

            panTilt.moveTo(nums);
        } else if (inputStr.startsWith("PAN")) {
            // Find step count for pan
            int num = inputStr.substring(3).toInt();
            pan.move(num);
            pan += num;
        } else if (inputStr.startsWith("TILT")) {
            // Find step count for tilt
            int num = inputStr.substring(4).toInt();
            tilt.move(num);
            tilt += num;
        } else if (inputStr.startsWith("ZERO_PAN")) {
            // Zero pan to set the current position to be home
            pan = 0;
        } else if (inputStr.startsWith("ZERO_TILT")) {
            // Zero tilt to set the current position to be home
            tilt = 0;
        } else if (inputStr.startsWith("RESTART")) {
            // Reset pan and tilt back to home
            panTilt.moveTo((const long[]){0, 0});
        } else {
            Serial.println("INVALID COMMAND");
        }

        // Block until pan and tilt have moved to target position
        while (panTilt.run());

        Serial.println("OK");
    }

    // pan.runToPosition();
    // tilt.runToPosition();
}

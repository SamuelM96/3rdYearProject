//#include <Adafruit_INA219.h>

#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Stepper.h>
#include <SPI.h>
#include <Wire.h>

#define MOTOR_STEPS 200

// All the wires needed for full functionality
#define DIR 6
#define STEP 7
#define CLK 3
#define DT 4

AccelStepper stepper(AccelStepper::DRIVER, STEP, DIR, 0, 0, true);
int encoderPosCount = 0;
int clkLast;
int clkVal;
boolean bCW;
//Adafruit_INA219 ina219;
//uint32_t currentFrequency;

void setup()
{
  Serial.begin(9600);

  //  ina219.begin();

  stepper.setMaxSpeed(100);
  stepper.setSpeed(100);
  // stepper.setAcceleration(100);

  // pinMode(CLK, INPUT);
  // pinMode(DT, INPUT);

  // clkLast = digitalRead(CLK);
  // Serial.println("testing");
}

void loop()
{
  // clkVal = digitalRead(CLK);

  // if (clkVal != clkLast)
  // {
  //   if (digitalRead(DT) != clkVal)
  //   {
  //     encoderPosCount++;
  //     bCW = true;
  //   }
  //   else
  //   {
  //     bCW = false;
  //     encoderPosCount--;
  //   }

  //   Serial.print("Rotated: ");
  //   if (bCW)
  //   {
  //     Serial.println("clockwise");
  //   }
  //   else
  //   {
  //     Serial.println("counterclockwise");
  //   }

  //   Serial.print("Encoder Position: ");
  //   Serial.println(encoderPosCount);
  //   stepper.moveTo(encoderPosCount * 5);
  //   stepper.setSpeed(100);
  // }

  //  float shuntvoltage = 0;
  //  float busvoltage = 0;
  //  float current_mA = 0;
  //  float loadvoltage = 0;
  //
  //  shuntvoltage = ina219.getShuntVoltage_mV();
  //  busvoltage = ina219.getBusVoltage_V();
  //  current_mA = ina219.getCurrent_mA();
  //  loadvoltage = busvoltage + (shuntvoltage / 1000);
  //
  //  Serial.print("Bus Voltage:   "); Serial.print(busvoltage); Serial.println(" V");
  //  Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage); Serial.println(" mV");
  //  Serial.print("Load Voltage:  "); Serial.print(loadvoltage); Serial.println(" V");
  //  Serial.print("Current:       "); Serial.print(current_mA); Serial.println(" mA");
  //  Serial.println("");
  //}

  // clkLast = clkVal;
  // stepper.runSpeedToPosition();
   long pos = stepper.currentPosition();
   long stepperSpeed = stepper.speed();
   if (stepperSpeed > 0 && pos >= 150 || stepperSpeed < 0 && pos <= 50) {
     stepper.setSpeed(-stepperSpeed);
   }

   stepper.runSpeed();
  //  stepper.runToNewPosition(0);
  //  stepper.runToNewPosition(235);
}

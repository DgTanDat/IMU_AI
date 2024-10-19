
#include "Arduino.h"

#ifndef MotorDriver_h

#define MotorDriver_h
#define MOTORLATCH 15
#define MOTORCLK 22
#define MOTORENABLE 18
#define MOTORDATA 17


// 8-bit bus after the 74HC595 shift register
// (not Arduino pins)
// These are used to set the direction of the bridge driver.
#define MOTOR1_A 2
#define MOTOR1_B 3
#define MOTOR2_A 1
#define MOTOR2_B 4
#define MOTOR3_A 5
#define MOTOR3_B 7
#define MOTOR4_A 0
#define MOTOR4_B 6

// Arduino pins for the PWM signals.
#define MOTOR1_PWM 16
#define MOTOR2_PWM 23
#define MOTOR3_PWM 19
#define MOTOR4_PWM 21

// Codes for the motor function.
#define FORWARD 1
#define BACKWARD 2
#define BRAKE 3
#define RELEASE 4


class MotorDriver
{

public:
	MotorDriver();
	void motor(int nMotor, int command, int speed);
private:
	void shiftWrite(int output, int high_low);
	void motor_output (int output, int high_low, int speed);
  
};

#endif

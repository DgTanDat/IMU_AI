from motorDriver import MotorDriver
import time

m = MotorDriver()

FORWARD = 1
BACKWARD = 2
BRAKE = 3
RELEASE = 4

def turnLeft(speed):
    m.motor(1, BACKWARD, speed)
    m.motor(2, BACKWARD, speed)
    m.motor(3, FORWARD, speed)
    m.motor(4, FORWARD, speed)

def turnRight(speed):
    m.motor(1, FORWARD, speed)
    m.motor(2, FORWARD, speed)
    m.motor(3, BACKWARD, speed)
    m.motor(4, BACKWARD, speed)

def forward(speed):
    m.motor(1, FORWARD, speed)
    m.motor(2, FORWARD, speed)
    m.motor(3, FORWARD, speed)
    m.motor(4, FORWARD, speed)

def backward(speed):
    m.motor(1, BACKWARD, speed)
    m.motor(2, BACKWARD, speed)
    m.motor(3, BACKWARD, speed)
    m.motor(4, BACKWARD, speed)

def brake(speed):
    m.motor(1, BRAKE, speed)
    m.motor(2, BRAKE, speed)
    m.motor(3, BRAKE, speed)
    m.motor(4, BRAKE, speed)

def release(speed):
    m.motor(1, RELEASE, speed)
    m.motor(2, RELEASE, speed)
    m.motor(3, RELEASE, speed)
    m.motor(4, RELEASE, speed)

if __name__ == "__main__":
    if not False:
        print("run motor")
    forward(100)
    time.sleep(10)
    turnRight(100)
    time.sleep(10)
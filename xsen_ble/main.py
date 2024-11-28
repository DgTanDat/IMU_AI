import simplepyble
import threading
import numpy as np
import math
import threading
from motorDriver import *

m = motorDriver.MotorDriver()

bleServerName = "Movella DOT"
STABLE_THREADHOLD = 8
NONE = -1

freq = 60
delta_t = 1/f 
count = 0
packageCounter = 3*f 

STOP = 1
GOSTRAIGHT = 2
TURNRIGHT = 3

threadhold = 0.05

positionX = 0
positionY = 0

startPosX = 0
startPosY = 0

curFaccX = 0
curFaccY = 0

lastFaccX = 0
lastFaccY = 0

counterX = 0
counterY = 0

curVelX = 0
curVelY = 0

lastVelX = 0
lastVelY = 0

initLastState = GOSTRAIGHT
initState = GOSTRAIGHT

focusYaw = 0
curYaw = 0
lastYaw = 0

isWrite = False
haveInitYaw = False
angle_thread_high = 0
angle_thread_low = 0

waitTime = 0

configServiceUUID = "15171000-4947-11e9-8646-d663bd873d93"
measurementServiceUUID = "15172000-4947-11e9-8646-d663bd873d93"

devicectrlCharacteristicUUID = "15171002-4947-11e9-8646-d663bd873d93"
measureCtrlCharacteristicUUID = "15172001-4947-11e9-8646-d663bd873d93"
medPayLoadCharacteristicUUID = "15172003-4947-11e9-8646-d663bd873d93"

notifyQueue = []
DATA_LENGTH = 4

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

def notifyProcess(data):
    chunks = [data[i:i+4] for i in range(0, len(data), 4)]

    notifyQueue.append(chunks)
    
    # print(f"Notification: {receiveDatas}")
   

def convertData(data, index):
    value = data[index]
    float_value = np.frombuffer(value, dtype=np.float32)
    return (float_value)

def cal_angle(angle, angular_turn):
    gap = 0
    temp = abs(angle + angular_turn)
    if temp <= 180: 
        return angle + angular_turn
    else:
        gap = temp - 180
        if angular_turn < 0:
            return float(180 - gap)
        else:
            return float(-180 + gap)

def cal_distance(x0, y0, x1, y1):
    temp = math.sqrt((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1))
    return temp

def processNotifyTask():
    staePN = GOSTRAIGHT
    lastStatePN = NONE
    while True:
        if notifyQueue != [] and lastStateQueue != []:
            notifyDatas = notifyQueue.pop(0)
            lastStatePN = lastStateQueue.pop(0)
            curYaw = convertData(notifyDatas, 3)
            faccX = convertData(notifyDatas, 4)
            faccY = convertData(notifyDatas, 5)

            if not haveInitYaw:
                focusYaw = curYaw
                haveInitYaw = True
                angle_thread_high = cal_angle(focusYaw, -89)
                angle_thread_low = cal_angle(focusYaw, -91)

            if lastStatePN == STOP:
                waitTime -= 1
                if waitTime <= 0:
                    staePN = GOSTRAIGHT
                else:
                    staePN = STOP
            elif lastStatePN == GOSTRAIGHT:
                if curFaccX in range(-threadhold, threadhold):
                    curFaccX = 0
                    counterX += 1
                else:
                    counterY = 0
                if curFaccY in range(-threadhold, threadhold):
                    curFaccY = 0
                    counterY += 1
                else:
                    counterY = 0

                if counterX >= STABLE_THREADHOLD:
                    curVelX = 0
                if counterY >= STABLE_THREADHOLD:
                    curVelY = 0

                curVelX += 0.5*(lastFaccX + curFaccX)*delta_t
                curVelY += 0.5*(lastFaccY + curFaccY)*delta_t

                positionX += 0.5*(lastVelX + curVelX)*delta_t
                positionY += 0.5*(lastVelY + curVelY)*delta_t

                if cal_distance(startPosX, startPosY, positionX, positionY) >= 0.7:
                    brake()
                    statePN = TURNRIGHT
                    startPosX = positionX
                    startPosY = positionY
                else:
                    statePN = GOSTRAIGHT

            elif lastStatePN == TURNRIGHT:
                if curYaw in range(angle_thread_low, angle_thread_high):
                    focusYaw = curYaw
                    angle_thread_high = cal_angle(focusYaw, -89)
                    angle_thread_low = cal_angle(focusYaw, -91)
                    statePN = STOP
                    positionX = 0
                    waitTime = 990
                else:
                    staePN = TURNRIGHT
            else:
                statePN = GOSTRAIGHT
        stateQueue.append(staePN)
        astYaw = curYaw
        lastFaccX = curFaccX
        lastFaccY = curFaccY
        lastVelX = curVelX
        lastVelY = curVelY

def startMeasurementTask():
    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")

    # # Query the user to pick an adapter
    # print("Please select an adapter:")
    # for i, adapter in enumerate(adapters):
    #     print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

    # choice = int(input("Enter choice: "))
    adapter = adapters[0]

    print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: print("Scan started."))
    adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
    adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

    # Scan for 5 seconds
    adapter.scan_for(5000)

    peripherals = adapter.scan_get_results()
    selectIndex = -1

    for index, peripheral in enumerate(peripherals):
        if peripheral.identifier() == bleServerName:
            selectIndex = index
        else:
            break

    peripheral = peripherals[selectIndex]

    print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
    peripheral.connect()

    print("Successfully connected")

    # start measurement
    start_mess = "010110"
    byteData = bytes.fromhex(start_mess)
    peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, bytes(byteData))
    
    contents = peripheral.notify(measurementServiceUUID, medPayLoadCharacteristicUUID, lambda data: notifyProcess(data))

def processStateTask():
    stateSP = NONE
    lastStateSP = NONE
    while True:
        if stateQueue != []:
            if lastStateSP != stateSP:
                if stateSP == STOP:
                    brake()
                elif stateSP == GOSTRAIGHT:
                    forward(250)
                elif stateSP == TURNRIGHT:
                    turnRight(180)
                else:
                    stateSP = STOP
                    brake()
                lastStateSP = stateSP
            lastStateQueue.append(lastStateSP)

if __name__ == "__main__":
    pmeasureTask = threading.Thread(target=startMeasurementTask)
    pstateTask = threading.Thread(target=processStateTask)
    pnotifyTask = threading.Thread(target=processNotifyTask)
    
    pmeasureTask.start()
    pstateTask.start()
    pnotifyTask.start()

    pmeasureTask.join()
    pstateTask.join()
    pnotifyTask.join()
    
    # while True:
    #     if notifyQueue != []:
    #         notifyDatas = notifyQueue.pop(0)
    #         yaw = convertData(notifyDatas, 3)
    #         faccX = convertData(notifyDatas, 4)
    #         faccY = convertData(notifyDatas, 5)

    #         print(f"raw data: {notifyDatas}")
    #         print(f"yaw: {yaw}")
    #         print(f"faccX: {faccX}")
    #         print(f"faccY: {faccY}")

   
    # Write the content to the characteristic
    # Note: `write_request` required the payload to be presented as a bytes object.
    

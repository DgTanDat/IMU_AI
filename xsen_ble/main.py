import math
import threading
import csv
from motorDriver import *
import simplepyble
import struct
from queue import Queue
import time

m = MotorDriver()

bleServerName = "Movella DOT"

STOP = 1
GOSTRAIGHT = 2
TURNRIGHT = 3
NONE = -1

freq = 60
delta_t = 1/freq 
packageCounter = 3*freq 
count = 0

configServiceUUID = "15171000-4947-11e9-8646-d663bd873d93"
measurementServiceUUID = "15172000-4947-11e9-8646-d663bd873d93"

devicectrlCharacteristicUUID = "15171002-4947-11e9-8646-d663bd873d93"
measureCtrlCharacteristicUUID = "15172001-4947-11e9-8646-d663bd873d93"
medPayLoadCharacteristicUUID = "15172003-4947-11e9-8646-d663bd873d93"

notifyQueue = Queue(maxsize = 60)
stateQueue = Queue(maxsize = 60)
lastStateQueue = Queue(maxsize = 60)

data = [
    ['faccX', 'faccY', 'yaw'],
]

def write_to_csv(filename, faccX, faccY, yaw):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([faccX, faccY, yaw])

def turnLeft(speed):
    m.motor(1, BACKWARD, speed)
    m.motor(2, BACKWARD, speed)
    m.motor(3, FORWARD, speed)
    m.motor(4, FORWARD, speed)
    print("motor tl")

def turnRight(speed):
    m.motor(1, FORWARD, speed)
    m.motor(2, FORWARD, speed)
    m.motor(3, BACKWARD, speed)
    m.motor(4, BACKWARD, speed)
    print("motor tr")

def forward(speed):
    m.motor(1, FORWARD, speed)
    m.motor(2, FORWARD, speed)
    m.motor(3, FORWARD, speed)
    m.motor(4, FORWARD, speed)
    print("motor fw")

def backward(speed):
    m.motor(1, BACKWARD, speed)
    m.motor(2, BACKWARD, speed)
    m.motor(3, BACKWARD, speed)
    m.motor(4, BACKWARD, speed)
    print("motor bw")

def brake():
    m.motor(1, BRAKE, 0)
    m.motor(2, BRAKE, 0)
    m.motor(3, BRAKE, 0)
    m.motor(4, BRAKE, 0)
    print("motor bk")

def release():
    m.motor(1, RELEASE, 0)
    m.motor(2, RELEASE, 0)
    m.motor(3, RELEASE, 0)
    m.motor(4, RELEASE, 0)

def notifyProcess(data):
    global count 
    if count >= packageCounter:
        notifyQueue.put(data)
    else:
        count += 1
    print(count)
   
def convertData(data, index):
    float_value = struct.unpack('<f', data[index:index+4])[0]
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

def processNotifyTask(peripheral):
    STABLE_THREADHOLD = 8
    global NONE
    global STOP 
    global GOSTRAIGHT 
    global TURNRIGHT
    global delta_t

    threadhold = 0.05

    statePN = NONE
    lastStatePN = NONE

    initLastState = GOSTRAIGHT
    initState = GOSTRAIGHT

    haveInitYaw = False
    angle_thread_high = 0
    angle_thread_low = 0

    waitTime = 0

    focusYaw = 0
    curYaw = 0
    lastYaw = 0

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

    while True:
        # if not lastStateQueue.empty() and notifyQueue.empty():
        #     if lastStateQueue.get() == STOP:

        if not notifyQueue.empty() and not lastStateQueue.empty():
            notifyDatas = notifyQueue.get()
            lastStatePN = lastStateQueue.get()
            curYaw = convertData(notifyDatas, 12)
            curFaccX = convertData(notifyDatas, 16)
            curFaccY = convertData(notifyDatas, 20)
            print(curYaw)
            print(curFaccX)
            print(curFaccY)
            write_to_csv('data_records.csv', curFaccX, curFaccY, curYaw)

            if not haveInitYaw:
                focusYaw = curYaw
                haveInitYaw = True
                angle_thread_high = cal_angle(focusYaw, -89)
                angle_thread_low = cal_angle(focusYaw, -91)

            if lastStatePN == STOP:
                print("in stop phase")
                waitTime -= 1
                if waitTime <= 0:
                    statePN = GOSTRAIGHT
                    waitTime = 0
                else:
                    if waitTime == 200:
                        start_mess = b'\x01\x01\x10'
                        peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, start_mess)
                        text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
                        print(text)
                        print(peripheral.is_connected())
                    statePN = STOP
            elif lastStatePN == GOSTRAIGHT:
                if curFaccX >= (-threadhold) and curFaccX <= threadhold:
                    curFaccX = 0
                    counterX += 1
                else:
                    counterX = 0
                if curFaccY >= (-threadhold) and curFaccY <= threadhold:
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

                if cal_distance(startPosX, startPosY, positionX, positionY) >= 0.4:
                    brake()
                    statePN = TURNRIGHT
                    startPosX = positionX
                    startPosY = positionY
                else:
                    statePN = GOSTRAIGHT

            elif lastStatePN == TURNRIGHT:
                if curYaw > angle_thread_low and curYaw < angle_thread_high:
                    focusYaw = curYaw
                    angle_thread_high = cal_angle(focusYaw, -89)
                    angle_thread_low = cal_angle(focusYaw, -91)
                    statePN = STOP
                    
                    stop_mess = b'\x00\x00\x10'
                    peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, stop_mess)
                    text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
                    print(text)
                    print(peripheral.is_connected())
                    waitTime = 240
                else:
                    statePN = TURNRIGHT
            else:
                statePN = GOSTRAIGHT
            stateQueue.put(statePN)
            lastYaw = curYaw
            lastFaccX = curFaccX
            lastFaccY = curFaccY
            lastVelX = curVelX
            lastVelY = curVelY    
        time.sleep(1e-6)

def processStateTask():
    global NONE
    global STOP 
    global GOSTRAIGHT 
    global TURNRIGHT
    stateSP = NONE
    lastStateSP = NONE
    while True:
        if not stateQueue.empty():
            stateSP = stateQueue.get()
            if lastStateSP != stateSP:
                if stateSP == STOP:
                    brake()
                elif stateSP == GOSTRAIGHT:
                    forward(100)
                    print("run fw")
                elif stateSP == TURNRIGHT:
                    turnRight(100)
                else:
                    stateSP = STOP
                    brake()
                lastStateSP = stateSP
            lastStateQueue.put(lastStateSP)
        time.sleep(1e-6)

if __name__ == "__main__":
    with open('data_records.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

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

    # Ensure the characteristic supports notifications before starting
    try:
        contents = peripheral.notify(measurementServiceUUID, medPayLoadCharacteristicUUID, lambda data: notifyProcess(data))
        print("Notifications started successfully.")
        text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
        print(text)
        start_mess = b'\x01\x01\x10'
        peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, start_mess)
        text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
        print(text)
        lastStateQueue.put(GOSTRAIGHT)
    except RuntimeError as e:
        print(f"Error starting notifications: {e}")
    

    # Keep the program running to listen for notifications
    try:
        pstateTask = threading.Thread(target=processStateTask)
        pnotifyTask = threading.Thread(target=processNotifyTask, args=(peripheral,))
    
        pstateTask.start()
        pnotifyTask.start()

        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting.")
    finally:
        peripheral.disconnect()
        print("Disconnected.")
    
    

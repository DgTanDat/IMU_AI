import threading
import numpy as np
import math
import threading
import csv
from motorDriver import *
import simplepyble
import struct
from queue import Queue

bleServerName = "Movella DOT"

configServiceUUID = "15171000-4947-11e9-8646-d663bd873d93"
measurementServiceUUID = "15172000-4947-11e9-8646-d663bd873d93"

devicectrlCharacteristicUUID = "15171002-4947-11e9-8646-d663bd873d93"
measureCtrlCharacteristicUUID = "15172001-4947-11e9-8646-d663bd873d93"
medPayLoadCharacteristicUUID = "15172003-4947-11e9-8646-d663bd873d93"

notifyQueue = Queue(maxsize = 60)
stateQueue = Queue(maxsize = 60)
lastStateQueue = Queue(maxsize = 60)

isWrite = False
lock = threading.Lock()

def notifyProcess(data):
    notifyQueue.put(data)

def task1(peripheral):
    count = 0
    isSend = False
    while True:
        if not notifyQueue.empty() and not lastStateQueue.empty():
            notifyDatas = notifyQueue.get()
            lastStatePN = lastStateQueue.get()
            stateQueue.put(lastStatePN)
            print(notifyDatas)
            print(peripheral.is_connected())
            if count == (5):
                if not isSend and peripheral.is_connected():
                    print("write ne")
                    isSend = True
                    start_mess = b'\x01\x00\x10'
                    peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, start_mess)
                    text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
                    print(text)
                    print(peripheral.is_connected())
            if count == (10):
                start_mess = b'\x01\x01\x10'
                peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, start_mess)
                text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
                print(text)
                print(peripheral.is_connected())
            count = count + 1
        time.sleep(1e-6)

def task2():
    while True:
        if not stateQueue.empty():
            state = stateQueue.get()
            lastStateQueue.put(state)
        time.sleep(1e-6)
    
if __name__ == "__main__":
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
        stateQueue.put(1)
    except RuntimeError as e:
        print(f"Error starting notifications: {e}")
    

    # Keep the program running to listen for notifications
    try:
        # time.sleep(5)
        # start_mess = b'\x01\x00\x10'
        # peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, start_mess)
        # text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
        # print(text)
        # print(peripheral.is_connected())
        # time.sleep(5)
        # start_mess = b'\x01\x01\x10'
        # peripheral.write_command(measurementServiceUUID, measureCtrlCharacteristicUUID, start_mess)
        # text = peripheral.read(measurementServiceUUID, measureCtrlCharacteristicUUID)
        # print(text)
        # print(peripheral.is_connected())
       
        # while True:
        #     if not isWrite:
        pmeasureTask = threading.Thread(target=task1, args=(peripheral,))
        pstateTask = threading.Thread(target=task2)
    
        pmeasureTask.start()
        pstateTask.start()
        
        while True:
            time.sleep(1)

        # pmeasureTask.join()
        # pstateTask.join()
            
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting.")
    finally:
        peripheral.disconnect()
        print("Disconnected.")
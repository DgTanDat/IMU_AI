import simplepyble
import threading
import numpy as np

bleServerName = "Movella DOT"

configServiceUUID = "15171000-4947-11e9-8646-d663bd873d93"
measurementServiceUUID = "15172000-4947-11e9-8646-d663bd873d93"

devicectrlCharacteristicUUID = "15171002-4947-11e9-8646-d663bd873d93"
measureCtrlCharacteristicUUID = "15172001-4947-11e9-8646-d663bd873d93"
medPayLoadCharacteristicUUID = "15172003-4947-11e9-8646-d663bd873d93"

notifyQueue = []
DATA_LENGTH = 4

def notifyProcess(data):
    chunks = [data[i:i+4] for i in range(0, len(data), 4)]

    notifyQueue.append(chunks)
    
    # print(f"Notification: {receiveDatas}")
   

def convertData(data, index):
    value = data[index]
    float_value = np.frombuffer(value, dtype=np.float32)
    return (float_value)


if __name__ == "__main__":
    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")

    # Query the user to pick an adapter
    print("Please select an adapter:")
    for i, adapter in enumerate(adapters):
        print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

    choice = int(input("Enter choice: "))
    adapter = adapters[choice]

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

    while True:
        if notifyQueue != []:
            notifyDatas = notifyQueue.pop(0)
            yaw = convertData(notifyDatas, 3)
            faccX = convertData(notifyDatas, 4)
            faccY = convertData(notifyDatas, 5)

            print(f"raw data: {notifyDatas}")
            print(f"yaw: {yaw}")
            print(f"faccX: {faccX}")
            print(f"faccY: {faccY}")

   
    # Write the content to the characteristic
    # Note: `write_request` required the payload to be presented as a bytes object.
    

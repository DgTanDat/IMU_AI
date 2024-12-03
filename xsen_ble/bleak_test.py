import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
import threading
import numpy as np
import struct

# Define the name of your BLE device
TARGET_DEVICE_NAME = "Movella DOT" 
TARGET_DEVICE_ADDRESS = ""

# Define UUIDs for services and characteristics (update with correct values)
configServiceUUID = "15171000-4947-11e9-8646-d663bd873d93"
measurementServiceUUID = "15172000-4947-11e9-8646-d663bd873d93"

devicectrlCharacteristicUUID = "15171002-4947-11e9-8646-d663bd873d93"
measureCtrlCharacteristicUUID = "15172001-4947-11e9-8646-d663bd873d93"
medPayLoadCharacteristicUUID = "15172003-4947-11e9-8646-d663bd873d93"

def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """Simple notification handler which prints the data received."""
    # print(data)
    
    # print(data[1])
    print("yaw: ", convertData(data, 12))
    print("faccX: ", convertData(data, 16))
    print("faccY: ", convertData(data, 20))

def convertData(data, index):
    float_value = struct.unpack('<f', data[index:index+4])[0]
    return (float_value)    

async def stopMeasurement(client):
    """Write to a characteristic."""
    byteData = bytearray([0x00, 0x00, 0x00])

    await client.write_gatt_char(measureCtrlCharacteristicUUID, byteData, response=True)
    print(f"Written value to {measureCtrlCharacteristicUUID}: {byteData}")

    await client.stop_notify(medPayLoadCharacteristicUUID)
    

async def startMeasurement(client):
    """Write to a characteristic."""
    byteData = bytearray([0x01, 0x01, 0x10])

    await client.write_gatt_char(measureCtrlCharacteristicUUID, byteData, response=True)
    print(f"Written value to {measureCtrlCharacteristicUUID}: {byteData}")

    await client.start_notify(medPayLoadCharacteristicUUID, notification_handler)   
    

async def main():
    # Scan for BLE devices
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    # Find the target device
    target_device = None
    for device in devices:
        print(f"Found device: {device.name} - {device.address}")
        if device.name == TARGET_DEVICE_NAME:
            target_device = device
            TARGET_DEVICE_ADDRESS = device.address
            break

    if not target_device:
        print(f"Device with name '{TARGET_DEVICE_NAME}' not found.")
        return

    print(f"Found target device: {target_device.name} - {target_device.address}")


    # Connect to the target device
    # async with BleakClient(TARGET_DEVICE_ADDRESS) as client:
    client = BleakClient(TARGET_DEVICE_ADDRESS)
    await client.connect()
        # Check if connected
    connected = await client.is_connected()
    if connected:
        print(f"Connected to {target_device.address}")
            
            # Subscribe to the characteristic notifications
           
        byteData = bytearray([0x01, 0x01, 0x10])

        await client.write_gatt_char(measureCtrlCharacteristicUUID, byteData, response=True)

        await client.start_notify(medPayLoadCharacteristicUUID, notification_handler)

        # Keep the connection alive to receive notifications
        data = bytearray([0x00, 0x01, 0x10])
        while True:
            await asyncio.sleep(10)  # Sleep here to keep the loop going
            await stopMeasurement(client)
            await asyncio.sleep(10)
            await startMeasurement(client)
            
    else:
        print(f"Failed to connect to {device_address}")

        # # Check if the service is available
        # services = await client.get_services()
        # if measurementServiceUUID not in [service.uuid for service in services]:
        #     print(f"Service {measurementServiceUUID} not found on device.")
        #     return

        # print(f"Service {measurementServiceUUID} is available.")


if __name__ == "__main__":
    asyncio.run(main())



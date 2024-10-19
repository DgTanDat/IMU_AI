#include <Arduino.h>
#include "BLEDevice.h"
#include "config.h"
#include "MotorDriver.h"
#include "math.h"

MotorDriver m;

/* UUID's of the service, characteristic that we want to read*/
// BLE Service
static BLEUUID configServiceUUID("15171000-4947-11E9-8646-D663BD873D93");
static BLEUUID measurementServiceUUID("15172000-4947-11E9-8646-D663BD873D93");
static BLEUUID batteryServiceUUID("15173000-4947-11E9-8646-D663BD873D93");

// BLE Characteristics
static BLEUUID deviceIn4CharacteristicUUID("15171001-4947-11E9-8646-D663BD873D93");
static BLEUUID devicectrlCharacteristicUUID("15171002-4947-11E9-8646-D663BD873D93");
static BLEUUID measureCtrlCharacteristicUUID("15172001-4947-11E9-8646-D663BD873D93");
static BLEUUID longPayLoadCharacteristicUUID("15172002-4947-11E9-8646-D663BD873D93");
static BLEUUID medPayLoadCharacteristicUUID("15172003-4947-11E9-8646-D663BD873D93");
static BLEUUID shortPayLoadCharacteristicUUID("15172004-4947-11E9-8646-D663BD873D93");

//Flags stating if should begin connecting and if the connection is up
static boolean doConnect = false;
static boolean connected = false;
static boolean doScan= false;

//Address of the peripheral device. Address will be found during scanning...
static BLEAddress *pServerAddress;
 
//Characteristicd that we want to read
static BLERemoteCharacteristic* ctrlCharacteristic;
static BLERemoteCharacteristic* medPayloadCharacteristic;

void turnLeft(int speed){
  m.motor(1, BACKWARD, speed);
  m.motor(2, BACKWARD, speed);
  m.motor(3, FORWARD, speed);
  m.motor(4, FORWARD, speed);
}

void turnRight(int speed){
  m.motor(1, FORWARD, speed);
  m.motor(2, FORWARD, speed);
  m.motor(3, BACKWARD, speed);
  m.motor(4, BACKWARD, speed);
}

void forward(int speed){
  m.motor(1, FORWARD, speed);
  m.motor(2, FORWARD, speed);
  m.motor(3, FORWARD, speed);
  m.motor(4, FORWARD, speed);
}

void backward(int speed){
  m.motor(1, BACKWARD, speed);
  m.motor(2, BACKWARD, speed);
  m.motor(3, BACKWARD, speed);
  m.motor(4, BACKWARD, speed);
}

void brake(){
  m.motor(1, BRAKE, 255);
  m.motor(2, BRAKE, 255);
  m.motor(3, BRAKE, 255);
  m.motor(4, BRAKE, 255);
}

void release(){
  m.motor(1, RELEASE, 255);
  m.motor(2, RELEASE, 255);
  m.motor(3, RELEASE, 255);
  m.motor(4, RELEASE, 255);
}

void timeStampConvert(uint8_t* data, int startIndex){
  uint32_t timeStamp = 0;
  for(int i=startIndex; i<DATA_LENGTH; i++){
    timeStamp |= data[i] << ((i) * 8);
  }
  Serial.print("TimeStamp is:");
  Serial.println(timeStamp);
}

float velocityCal(float freeAcc, float deltaTime){
  if(freeAcc < 0.05 && freeAcc > -0.05) return 0;
  else return 0.5*(freeAcc * deltaTime * deltaTime);
}

float dataConvert(uint8_t* data, int startIndex){
  union IntFloat temp;
  temp.i = 0;
  int count = 0;
  for(int i=startIndex; i<startIndex+DATA_LENGTH; i++){
    temp.i |= data[i] << ((count) * 8);
    count++;
  }
  Serial.println(temp.f);
  return temp.f;
}

static float focusYaw = 0;
static float yaw = 0;
bool calibFlag = false;

bool isWrite = false;
bool isForward = true;
bool isTurn = false;
bool haveInitYaw = false;
float angle_thread_high;
float angle_thread_low;

float cal_angle(float angle, float angular_turn){
  float gap = 0;
  float temp = fabs(angle + angular_turn);
  if(temp <= 180) return angle + angular_turn;
  else{
    gap = temp - 180;
    if(angular_turn < 0){
      return float(180 - gap);
    }
    else{
      return float(-180 + gap);
    }
  }
}

//When the BLE Server sends a new temperature reading with the notify property
static void NotifyCallback(BLERemoteCharacteristic* pBLERemoteCharacteristic, 
                                        uint8_t* pData, size_t length, bool isNotify) {
  if(pBLERemoteCharacteristic->getUUID().toString() == medPayLoadCharacteristicUUID.toString()) 
  {
      Serial.print("Characteristic (Notify) from server: ");
      for(int i = 0; i<length; i++) {
        Serial.print(pData[i]);
        Serial.print('.');
      }
      Serial.println();  

      timeStampConvert(pData, 0);
      Serial.print("x_euler_e:");
      dataConvert(pData, 4);
      Serial.print("y_euler_e:");
      dataConvert(pData, 8);
      Serial.print("z_euler_e:");
      yaw = dataConvert(pData, 12);
      Serial.print("x acc:");
      accX = dataConvert(pData, 16);
      Serial.print("y acc:");
      accY = dataConvert(pData, 20);
      Serial.print("z acc:");
      accZ = dataConvert(pData, 24);

      accZ = accZ - 0.33;
      if(!calibFlag){
        if((fabs(accX) <= threadhold1) && (fabs(accY) <= threadhold1) && (fabs(accZ) <= threadhold1)) calibFlag = true;
      }
      
      if(calibFlag){
        if(!haveInitYaw){
          focusYaw = yaw;
          haveInitYaw = true;
          angle_thread_high = cal_angle(focusYaw, -88.5);
          angle_thread_low = cal_angle(focusYaw, -91.5);
        }
        if(!isForward){
          if(!isTurn){
            turnRight(180);
            isTurn = true;
          }
        }
        
        if((angle_thread_low <= yaw) && (yaw <= angle_thread_high)){
          brake();
          isForward = true;
          isTurn = false;
          focusYaw = yaw;
          angle_thread_high = cal_angle(focusYaw, -89);
          angle_thread_low = cal_angle(focusYaw, -91); 
        }

        if(fabs(accX) <= threadhold){
          accX = 0;
          curVecX = 0;
        }
        if(fabs(accY) <= threadhold){
          accY = 0;
          curVecY = 0;
        } 
        if(fabs(accZ) <= threadhold){
          accZ = 0;
          curVecZ = 0;
        } 

        // Serial.println(accX);
        // Serial.println(accY);
        // Serial.println(accZ);
        // curVecX += accX*delta_t;
        // curVecY += accY*delta_t;
        // curVecZ += accZ*delta_t;
        // positionX += delta_t*curVecX;
        // Serial.print("x position: ");
        // Serial.println(positionX);
        // positionY += delta_t*curVecY;
        // Serial.print("y position: ");
        // Serial.println(positionY);
        // positionZ += delta_t*curVecZ;
        // Serial.print("z position: ");
        // Serial.println(positionZ);
      }
  }
}

//Activate notify

bool connectCharacteristic(BLERemoteService* pRemoteService, BLERemoteCharacteristic* l_BLERemoteChar) {
  // Obtain a reference to the characteristic in the service of the remote BLE server.
  if (l_BLERemoteChar == nullptr) {
    Serial.print("Failed to find one of the characteristics");
    Serial.print(l_BLERemoteChar->getUUID().toString().c_str());
    return false;
  }
  Serial.println(" - Found characteristic: " + String(l_BLERemoteChar->getUUID().toString().c_str()));

  if(l_BLERemoteChar->canNotify()){
    l_BLERemoteChar->registerForNotify(NotifyCallback);
    Serial.println("notify register");
  }

  return true;
}
//Connect to the BLE Server that has the name, Service, and Characteristics
bool connectToServer(BLEAddress pAddress) {
   BLEClient* pClient = BLEDevice::createClient();
 
  // Connect to the remove BLE Server.
  pClient->connect(pAddress);
  Serial.println(" - Connected to server");
 
  // Obtain a reference to the service we are after in the remote BLE server.
  BLERemoteService* pRemoteService = pClient->getService(measurementServiceUUID);
  if (pRemoteService == nullptr) {
    Serial.print("Failed to find our service UUID: ");
    Serial.println(measurementServiceUUID.toString().c_str());
    return (false);
  }
 
  // Obtain a reference to the characteristics in the service of the remote BLE server.
  ctrlCharacteristic = pRemoteService->getCharacteristic(measureCtrlCharacteristicUUID);
  medPayloadCharacteristic = pRemoteService->getCharacteristic(medPayLoadCharacteristicUUID);


  if (ctrlCharacteristic == nullptr || medPayloadCharacteristic == nullptr) {
    Serial.print("Failed to find our characteristic UUID");
    return false;
  }
  if(connectCharacteristic(pRemoteService, ctrlCharacteristic) == false || connectCharacteristic(pRemoteService, medPayloadCharacteristic) == false)
    connected = false;
  Serial.println(" - Found our characteristics");
  return true;
}

//Callback function that gets called, when another device's advertisement has been received
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    if (advertisedDevice.getName() == bleServerName) { //Check if the name of the advertiser matches
      advertisedDevice.getScan()->stop(); //Scan can be stopped, we found what we are looking for
      pServerAddress = new BLEAddress(advertisedDevice.getAddress()); //Address of advertiser is the one we need
      doConnect = true; //Set indicator, stating that we are ready to connect
      Serial.println("Device found. Connecting!");
      BLEAddress temp = advertisedDevice.getAddress();
      Serial.println(temp.toString().c_str());
    }
  }
};
 


void setup() {
  
  //Start serial communication
  Serial.begin(115200);
  Serial.println("Starting Arduino BLE Client application...");


  //Init BLE device
  BLEDevice::init("");
 
  // // Retrieve a Scanner and set the callback we want to use to be informed when we
  // // have detected a new device.  Specify that we want active scanning and start the
  // // scan to run for 30 seconds.
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->start(30);
  // forward(255);
  // delay(2100);
  // brake();
  // delay(1000);
  // turnRight(255);
  // delay(800);
  // brake();
}


void loop() {
  // If the flag "doConnect" is true then we have scanned for and found the desired
  // BLE Server with which we wish to connect.  Now we connect to it.  Once we are
  // connected we set the connected flag to be true.
  std::uint8_t txValue[3];
  txValue[0] = 1;
  txValue[1] = 1;
  txValue[2] = 16;
  if (doConnect == true) {
    if (connectToServer(*pServerAddress)) {
      Serial.println("We are now connected to the BLE Server.");
      
      connected = true;
      if(!isWrite){
        ctrlCharacteristic->writeValue(txValue, 3);
        isWrite = true;
      }
    } else {
      Serial.println("We have failed to connect to the server; Restart your device to scan for nearby BLE server again.");
    }
    doConnect = false;
  }

 
  if(isForward){
    forward(255);
    delay(2100);
    brake();
    delay(1000);
    isForward = false;
  }

  
  // if(count < 3){
  //   forward(255);
  // } else if(count < 6){
  //   backward(255);
  // } else if(count < 9){
  //   turnLeft(255);
  // } else if(count < 12){
  //   turnRight(255);
  // } else if(count < 15){
  //   brake();
  // } else{
  //   count = 0;
  // }
  // count++;
  delay(1000); // Delay a second between loops.
}
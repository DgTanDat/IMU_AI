#include <Arduino.h>
#include "BLEDevice.h"
#include "config.h"
#include "MotorDriver.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "math.h"

QueueHandle_t notifyQueue;
QueueHandle_t stateQueue;
QueueHandle_t lastStateQueue;

MotorDriver m;
NotifyData notifyDatacb;

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

//Address of the peripheral device. Address will be found during scanning...
static BLEAddress *pServerAddress;
 
//Characteristicd that we want to read
static BLERemoteCharacteristic* ctrlCharacteristic;
static BLERemoteCharacteristic* medPayloadCharacteristic;
// static BLERemoteCharacteristic* deviceCtrlCharacteristic;

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

// void timeStampConvert(uint8_t* data, int startIndex){
//   uint32_t timeStamp = 0;
//   for(int i=startIndex; i<DATA_LENGTH; i++){
//     timeStamp |= data[i] << ((i) * 8);
//   }
//   Serial.print("TimeStamp is:");
//   Serial.println(timeStamp);
// }

// float velocityCal(float freeAcc, float deltaTime){
//   if(freeAcc < 0.05 && freeAcc > -0.05) return 0;
//   else return 0.5*(freeAcc * deltaTime * deltaTime);
// }

float dataConvert(uint8_t* data, int startIndex){
  union IntFloat temp;
  temp.i = 0;
  int count = 0;
  for(int i=startIndex; i<startIndex+DATA_LENGTH; i++){
    temp.i |= data[i] << ((count) * 8);
    count++;
  }
  // Serial.println(temp.f);
  return temp.f;
}

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

float cal_distance(float x0, float y0, float x1, float y1){
  return sqrt((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1));
}

//When the BLE Server sends a new temperature reading with the notify property
static void NotifyCallback(BLERemoteCharacteristic* pBLERemoteCharacteristic, 
                                        uint8_t* pData, size_t length, bool isNotify) {
  if(pBLERemoteCharacteristic->getUUID().toString() == medPayLoadCharacteristicUUID.toString()) 
  {
      // Serial.print("Characteristic (Notify) from server: ");
      // for(int i = 0; i<length; i++) {
      //   Serial.print(pData[i]);
      //   Serial.print('.');
      // }
      // Serial.println();  

      if(count >= packageCounter){
        memcpy(notifyDatacb.pData, pData, length);
        notifyDatacb.length = length;

        xQueueSend(notifyQueue, &notifyDatacb, portMAX_DELAY);
      }
      else count = count + 1;
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
  // BLERemoteService* pRemoteService0 = pClient->getService(configServiceUUID);
  // if (pRemoteService0 == nullptr) {
  //   Serial.print("Failed to find configuration service UUID: ");
  //   Serial.println(configServiceUUID.toString().c_str());
  //   return (false);
  // }

  BLERemoteService* pRemoteService1 = pClient->getService(measurementServiceUUID);
  if (pRemoteService1 == nullptr) {
    Serial.print("Failed to find measurement service UUID: ");
    Serial.println(measurementServiceUUID.toString().c_str());
    return (false);
  }
 
  // Obtain a reference to the characteristics in the service of the remote BLE server.
  // deviceCtrlCharacteristic = pRemoteService0->getCharacteristic(devicectrlCharacteristicUUID);
  ctrlCharacteristic = pRemoteService1->getCharacteristic(measureCtrlCharacteristicUUID);
  medPayloadCharacteristic = pRemoteService1->getCharacteristic(medPayLoadCharacteristicUUID);


  if (ctrlCharacteristic == nullptr || medPayloadCharacteristic == nullptr) {
    Serial.print("Failed to find our characteristics UUID");
    return false;
  }

  if(connectCharacteristic(pRemoteService1, ctrlCharacteristic) == false || 
  connectCharacteristic(pRemoteService1, medPayloadCharacteristic) == false)
    connected = false;
  Serial.println(" - Found measurement characteristics");
  
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
 
void processNotifyTask(void *parameter) {
  NotifyData notifyData;
  int statePN = GOSTRAIGHT;
  int lastStatePN;
  while (true) {
    if ((xQueueReceive(notifyQueue, &notifyData, portMAX_DELAY) == pdPASS)
    &&(xQueueReceive(lastStateQueue, &lastStatePN, portMAX_DELAY) == pdPASS)) {
      
      curYaw = dataConvert(notifyData.pData, 12);
      curFaccX = dataConvert(notifyData.pData, 16);
      curFaccY = dataConvert(notifyData.pData, 20);

      if(!haveInitYaw){
        focusYaw = curYaw;
        haveInitYaw = true;
        angle_thread_high = cal_angle(focusYaw, -89);
        angle_thread_low = cal_angle(focusYaw, -91);
      }
      switch (lastStatePN)
      {
        case STOP:
          waitTime -= 1;
          if(waitTime <= 0){
            statePN = GOSTRAIGHT;
          }
          else{
            statePN = STOP;
          }
          break;
        case GOSTRAIGHT:
          if((-threadhold <= curFaccX)&&(curFaccX <= threadhold)){
            curFaccX = 0;
            counterX++;
          }
          else{
            counterX = 0;
          }
          if((-threadhold <= curFaccY)&&(curFaccY <= threadhold)){
            curFaccY = 0;
            counterY++;
          }
          else{
            counterY = 0;
          }  
          if(counterX >= STABLE_THREADHOLD){
            curVelX = 0;
          }
          if(counterY >= STABLE_THREADHOLD){
            curVelY = 0;
          }

          curVelX += 0.5*(lastFaccX + curFaccX)*delta_t;
          curVelY += 0.5*(lastFaccY + curFaccY)*delta_t;
          
          positionX += 0.5*(lastVelX + curVelX)*delta_t;
          positionY += 0.5*(lastVelY + curVelY)*delta_t;

          if(cal_distance(startPosX, startPosY, positionX, positionY) >= 0.7){
            brake();
            statePN = TURNRIGHT;
            startPosX = positionX;
            startPosY = positionY;
          }
          else{
            statePN = GOSTRAIGHT;
          }
          break;
        case TURNRIGHT:
          if((angle_thread_low <= curYaw) && (curYaw <= angle_thread_high)){
            focusYaw = curYaw;
            angle_thread_high = cal_angle(focusYaw, -89);
            angle_thread_low = cal_angle(focusYaw, -91); 
            statePN = STOP; 
            positionX = 0;
            waitTime = 990;
          }
          else{
            statePN = TURNRIGHT;
          }
          
          break;
        default:
          statePN = GOSTRAIGHT;
          break;
      }
      xQueueSend(stateQueue, &statePN, portMAX_DELAY);
      lastYaw = curYaw;
      lastFaccX = curFaccX;
      lastFaccY = curFaccY;
      lastVelX = curVelX;
      lastVelY = curVelY;
    }
  }
}

void startXsenMeasurementTask(void *parameter) {
  while (true)
  {
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
    delay(1000);
  }
}

void stateProcessTask(void *parameter) {
  int stateSP = NONE;
  int lastStateSP = NONE;
  while (true)
  {
    if (xQueueReceive(stateQueue, &stateSP, portMAX_DELAY) == pdPASS) {
      if(lastStateSP != stateSP){
        switch (stateSP)
        {
          case STOP:
            brake();
            break;
          case GOSTRAIGHT:
            forward(250);
            break;
          case TURNRIGHT:
            turnRight(80);
            break;
          default:
            stateSP = STOP;
            brake();
            break;
        }
        lastStateSP = stateSP;
      }
      xQueueSend(lastStateQueue, &lastStateSP, portMAX_DELAY);
    }
  }
}

void setup() {
  
  Serial.begin(115200);
  Serial.println("Starting Arduino BLE Client application...");

  //Init BLE device
  BLEDevice::init("");
 
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->start(30);

  notifyQueue = xQueueCreate(10, sizeof(NotifyData)); 
  stateQueue = xQueueCreate(10, sizeof(int));
  lastStateQueue = xQueueCreate(10, sizeof(int));

  xQueueSend(lastStateQueue, &initLastState, portMAX_DELAY);

  xTaskCreate(startXsenMeasurementTask, "startXsenMeasurementTask", 4000, NULL, 1, NULL);
  xTaskCreate(processNotifyTask, "ProcessNotifyTask", 6000, NULL, 2, NULL);
  xTaskCreate(stateProcessTask, "stateProcessTask", 6000, NULL, 2, NULL);
}


void loop() {
}
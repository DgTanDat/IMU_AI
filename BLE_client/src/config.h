
//BLE Server name (the other ESP32 name running the server sketch)
#define bleServerName "Movella DOT"
#define DATA_LENGTH 4
#define STABLE_THREADHOLD 8
#define NONE -1

float f = 60;
float delta_t = 1/f;
static int count = 0;


const int packageCounter = 3*f;

union IntFloat {
    unsigned int i;
    float f;
};

struct NotifyData {
  uint8_t pData[32]; // Thay đổi kích thước phù hợp với length của notify
  size_t length;
};

enum{
  STOP,
  GOSTRAIGHT,
  TURNRIGHT,
};

const float threadhold = 0.05;

float positionX = 0;
float positionY = 0;
// static float positionZ = 0;

float startPosX = 0;
float startPosY = 0;

float curFaccX = 0;
float curFaccY = 0;
// float curFaccZ = 0;
float lastFaccX = 0;
float lastFaccY = 0;
// float lastFaccZ = 0;

int counterX = 0;
int counterY = 0;
// int counterZ = 0;

float curVelX = 0;
float curVelY = 0;
// float curVelZ = 0;
float lastVelX = 0;
float lastVelY = 0;
// float lastVelZ = 0;

int initLastState = GOSTRAIGHT;
int initState = GOSTRAIGHT;

float focusYaw = 0;
float curYaw = 0;
float lastYaw = 0;

bool isWrite = false;
bool haveInitYaw = false;
float angle_thread_high;
float angle_thread_low;

int waitTime = 0;
import random
import math

def cal_angular(angular, angular_turn):
    gap = 0
    temp = abs(angular + angular_turn)
    if temp <= 180:
        return angular + angular_turn
    else:
        gap = temp - 180
        if angular_turn < 0:
            return 180 - gap
        else:
            return -180 + gap

# Test the function 10 times with random angular values and angular_turn = 90
angular_turn = -90
for _ in range(10):
    random_angular = random.uniform(-180, 180)
    result = cal_angular(random_angular, angular_turn)
    print(f"angular = {random_angular:.2f}, result = {result:.2f}")
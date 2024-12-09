# importing csv module

import matplotlib.pyplot as plt
import csv

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')

# csv file name
filename = "record2.csv"

f = 60
delta_t = 1/f
threadhold = 0.05

packCounter =[]
counterPack = 0

faccX = []
faccY = [] 
yaw = []

accX = []
accY = []

velX = []
velY = []


cur_accX = 0
cur_accY = 0


cur_velX = 0
cur_velY = 0


rposX = []
rposY = []
rvelX = []
rvelY = []

posX = []
posY = []


isturn = []

cur_posX = 0
cur_posY = 0


start_posX = 0
start_posY = 0


counter = 0
step = f * 3
counterX = 0
counterY = 0

sample = 8
counter_turn = 0
counter_forward = 0
# i = []
timer_wait_stable = 0

def cal_distance(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1))**(0.5)

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields = next(csvreader)
    
    for row in csvreader:  
        
        faccX.append(float(row[0]))
        faccY.append(float(row[1]))
        yaw.append(float(row[2]))
        rposX.append(float(row[3]))
        rposY.append(float(row[4]))
        rvelX.append(float(row[5]))
        rvelY.append(float(row[6]))
        counter = counter+1

        if counter >= step:
            if abs(float(row[0])) <= threadhold:
                cur_accX = 0
                counterX += 1
            else:
                cur_accX = float(row[0])
                counterX = 0           

            if abs(float(row[1])) <= threadhold:
                cur_accY = 0
                counterY += 1
            else:
                cur_accY = float(row[1])
                counterY = 0    

            if counterX >= sample:
                cur_velX = 0
            if counterY >= sample:
                cur_velY = 0

            if int(yaw[counter-2]) != int(yaw[counter-1]):
                counter_turn += 1
                counter_forward = 0
            else:
                counter_forward += 1
                if counter_forward >= 10:
                    counter_turn = 0
            if(counter_turn >= 40):
                timer_wait_stable = 240
                isturn.append(1)
            else:
                isturn.append(-1)

            if timer_wait_stable > 0:          
                cur_accX = 0
                cur_accY = 0

                cur_velX = 0
                cur_velY = 0

                accX.append(0)
                accY.append(0)

                velX.append(0)
                velY.append(0)

                timer_wait_stable -= 1
            else:
                cur_velX += 0.5*(cur_accX + accX[counter-2])*delta_t
                cur_velY += 0.5*(cur_accY + accY[counter-2])*delta_t

                cur_posX += 0.5*(cur_velX + velX[counter-2])*delta_t
                cur_posY += 0.5*(cur_velY + velY[counter-2])*delta_t
    
                accX.append(cur_accX)
                accY.append(cur_accY)

                velX.append(cur_velX)
                velY.append(cur_velY)

            # cur_velX += cur_accX*delta_t
            # cur_velY += cur_accY*delta_t
            # cur_velZ += cur_accZ*delta_t

            # cur_posX += cur_velX*delta_t
            # cur_posY += cur_velY*delta_t
            # cur_posZ += cur_velZ*delta_t   
            posX.append(cur_posX)
            posY.append(cur_posY)
            
        else:
            isturn.append(-1)
            accX.append(0)
            accY.append(0)
           

            velX.append(0)
            velY.append(0)
            
    
            posX.append(0)
            posY.append(0)
            
        
       

# ax.scatter(posX, posY, posZ, c='blue', marker = 'o')
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')
# plt.show()

figure, axis = plt.subplots(2, 2)


axis[0, 0].plot(range(len(faccX)), accX, color = 'g',  
         marker = 'o', label='acc')
# axis[0, 0].plot(packCounter, isturn, color = 'r',  
#          marker = 'o', label='vel')
# axis[0, 0].plot(packCounter, posX, color = 'b',  
#          marker = 'o', label='pos')
axis[0, 0].set_title("x")


axis[0, 1].plot(range(len(faccY)), accY, color = 'g',  
         marker = 'o', label='acc')
# axis[0, 1].plot(packCounter, isturn, color = 'r',  
#          marker = 'o', label='vel')
# axis[0, 1].plot(packCounter, posY, color = 'b',  
#          marker = 'o', label='pos')
axis[0, 1].set_title("y")


axis[1, 0].plot(rposX, rposY, color = 'g',  
         marker = 'o', label='acc')
# axis[1, 0].plot(packCounter, isturn, color = 'r',  
#          marker = 'o', label='vel')
# axis[1, 0].plot(packCounter, posZ, color = 'b',  
#          marker = 'o', label='pos')
axis[1, 0].set_title("rPos")
# axis[1, 0].set_xlabel('x')
# axis[1, 0].set_ylabel('y')

axis[1, 1].plot(posX, posY, color = 'g',  
         marker = 'o', label='x')
# axis[1, 1].plot(packCounter, posX, color = 'r',  
#          marker = 'o', label='y')
# axis[1, 1].plot(packCounter, posY, color = 'b',  
#          marker = 'o', label='z')
# axis[1, 1].plot(packCounter, isturn, color = 'm',  
#          marker = 'o', label='z')
axis[1, 1].set_title("yaw")
# axis[1, 1].set_xlabel('x')
# axis[1, 1].set_ylabel('y')
 
# axis[0, 0].set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000])
# axis[0, 1].set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000])
# # axis[1, 0].set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000])
# axis[1, 1].set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000])

# axis[0, 0].set_yticks([-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,-0.5,0,0.5,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
# axis[0, 1].set_yticks([-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,-0.5,0,0.5,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
# # axis[1, 0].set_yticks([-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,-0.5,0,0.5,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])

# plt.xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000])  
# plt.yticks([-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,-0.5,0,0.5,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])  
# plt.plot(range(len(faccX)), faccX, color = 'm',  
#          marker = 'o',label = "e")
# plt.plot(range(len(faccY)), faccY, color = 'g',  
#          marker = 'o',label = "f") 
# plt.plot(packCounter, velX, color = 'r', 
#          marker = 'o',label = "v") 
# plt.plot(packCounter, posX, color = 'b', 
#          marker = 'o',label = "p") 

# plt.plot(posX, posY, color = 'g',  
#          marker = 'o',label = "acc") 
# # plt.plot(packCounter, velZ, color = 'r', 
# #          marker = 'o',label = "vel") 
# # plt.plot(packCounter, posZ, color = 'b', 
# #          marker = 'o',label = "pos") 

# plt.xlabel("x")
# plt.ylabel("y")
# plt.grid() 
# plt.legend() 
plt.show() 

 
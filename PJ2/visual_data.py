# importing csv module

import matplotlib.pyplot as plt
import csv

# csv file name
filename = "d2a.csv"

f = 60
delta_t = 1/f
threadhold = 0.05

packCounter = [] 
timeStamp = []
eulerX = [] 
eulerY = []
eulerZ = [] 
faccX = []
faccY = [] 
faccZ = []

accX = []
accY = [] 
accZ = []

velX = []
velY = []
velZ = []

cur_accX = 0
cur_accY = 0
cur_accZ = 0

cur_velX = 0
cur_velY = 0
cur_velZ = 0

posX = []
posY = []
posZ = []

cur_posX = 0
cur_posY = 0
cur_posZ = 0
counter = 0
step = f * 3
counterX = 0
counterY = 0
counterZ = 0
sample = 8
# i = []

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields = next(csvreader)

    for row in csvreader: 
        packCounter.append(row[0]) 
        timeStamp.append(row[1]) 
        eulerX.append(float(row[2]))
        eulerY.append(float(row[3]))
        eulerZ.append(float(row[4]))
        faccX.append(float(row[5]))
        faccY.append(float(row[6]))
        faccZ.append(float(row[7])-0.33)
         
        counter = counter+1

        if counter >= step:
            if abs(float(row[5])) <= threadhold:
                cur_accX = 0
                counterX += 1
            else:
                cur_accX = float(row[5])
                counterX = 0

            accX.append(cur_accX)

            if abs(float(row[6])) <= threadhold:
                cur_accY = 0
                counterY += 1
            else:
                cur_accY = float(row[6])
                counterY = 0

            accY.append(cur_accY)

            if abs(float(row[7])-0.33) <= threadhold:
                cur_accZ = 0
                counterZ += 1
            else: 
                cur_accZ = (float(row[7])-0.33)
                counterZ = 0

            accZ.append(cur_accZ)


        #     cur_posX += cur_velX*delta_t
        #     cur_posY += cur_velY*delta_t
        #     cur_posZ += cur_velZ*delta_t

        #     posX.append(cur_posX)
        #     posY.append(cur_posY)
        #     posZ.append(cur_posZ)
        else:
            accX.append(0)
            accY.append(0)
            accZ.append(0)
        #     velX.append(0)
        #     velY.append(0)
        #     velZ.append(0)
        #     posX.append(0)
        #     posY.append(0)
        #     posZ.append(0)
        if counterX >= sample:
            cur_velX = 0
        if counterY >= sample:
            cur_velY = 0
        if counterZ >= sample:
            cur_velZ = 0

        cur_velX += 0.5*cur_accX*delta_t
        cur_velY += 0.5*cur_accY*delta_t
        cur_velZ += 0.5*cur_accZ*delta_t

        cur_posX += 0.5*cur_velX*delta_t
        cur_posX += 0.5*cur_velX*delta_t
        cur_posX += 0.5*cur_velX*delta_t

        velX.append(cur_velX)
        velY.append(cur_velY)
        velZ.append(cur_velZ)

        posX.append(cur_posX)
        posY.append(cur_posY)
        posZ.append(cur_posZ)
        
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)

#     # get total number of rows
#     print("Total no. of rows: %d" % (csvreader.line_num))

# # printing the field names
# print('Field names are:' + ', '.join(field for field in fields))

# # printing first 5 rows
# print('\nFirst 5 rows are:\n')
# for row in rows[:5]:
#     # parsing each column of a row
#     for col in row:
#         print("%10s" % col, end=" "),
#     print('\n')


# figure, axis = plt.subplots(2, 2)


# axis[0, 0].plot(packCounter, accX, color = 'g',  
#          marker = 'o', label='Y')
# axis[0, 0].set_title("facc")


# axis[0, 1].plot(packCounter, velX, color = 'g',  
#          marker = 'o', label='Y')
# axis[0, 1].set_title("vel")


# axis[1, 0].plot(packCounter, posX, color = 'g',  
#          marker = 'o', label='Y')
# axis[1, 0].set_title("Pos")
 
# axis[0, 0].set_xticks([0, 250, 500, 750, 1000, 1250, 1500])
# axis[0, 1].set_xticks([0, 250, 500, 750, 1000, 1250, 1500])
# axis[1, 0].set_xticks([0, 250, 500, 750, 1000, 1250, 1500])

plt.xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000])  
plt.yticks([-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,-0.5,0,0.5,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])  
# plt.plot(packCounter, faccX, color = 'g',  
#          marker = 'o',label = "faccX") 
# plt.plot(packCounter, faccY, color = 'r', 
#          marker = 'o',label = "faccY") 
# plt.plot(packCounter, faccZ, color = 'b', 
#          marker = 'o',label = "faccZ") 

plt.plot(packCounter, accX, color = 'g',  
         marker = 'o',label = "acc") 
plt.plot(packCounter, velX, color = 'r', 
         marker = 'o',label = "vel") 
plt.plot(packCounter, posX, color = 'b', 
         marker = 'o',label = "pos") 
plt.grid() 
plt.legend() 
plt.show() 

# plt.xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]) 
# # plt.yticks([-200, -180, -150, -100, -50, 0, 50, 100, 150, 180, 200]) 
# plt.yticks([-10, -8, -6, -4, -2, -1,-0.5,0,0.5,1,2,4,6,8,10])
# plt.plot(a, g, color = 'g',  
#          marker = 'o',label = "dvX") 
# plt.plot(a, h, color = 'r', 
#          marker = 'o',label = "dvY") 
# plt.plot(a, i, color = 'b', 
#          marker = 'o',label = "dvZ") 
# plt.grid() 
# plt.legend() 
# plt.show() 
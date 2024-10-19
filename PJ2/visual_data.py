# importing csv module

import matplotlib.pyplot as plt
import csv

# csv file name
filename = "xsen_d2a.csv"

delta_t = 0.05
threadhold = 0.05

packCounter = [] 
timeStamp = []
eulerX = [] 
eulerY = []
eulerZ = [] 
faccX = []
faccY = [] 
faccZ = []

velX = []
velY = []
velZ = []

cur_velX = 0
cur_velY = 0
cur_velZ = 0

posX = []
posY = []
posZ = []

cur_posX = 0
cur_posY = 0
cur_posZ = 0

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

        if abs(float(row[5])) <= threadhold:
            cur_velX = 0
        else:
            cur_velX += float(row[5])*delta_t
        
        velX.append(float(cur_velX))

        if abs(float(row[6])) <= threadhold:
            cur_velY = 0
        else:
            cur_velY += float(row[6])*delta_t
        
        velY.append(float(cur_velY))
        
        if abs(float(row[7])-0.33) <= threadhold:
            cur_velZ = 0
        else:
            cur_velZ += (float(row[7])-0.33)*delta_t
        
        velZ.append(float(cur_velZ))

        cur_posX += cur_velX*delta_t
        cur_posY += cur_velY*delta_t
        cur_posZ += cur_velZ*delta_t

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


# axis[0, 0].plot(packCounter, faccY, color = 'g',  
#          marker = 'o', label='Y')
# axis[0, 0].set_title("facc")


# axis[0, 1].plot(packCounter, velY, color = 'g',  
#          marker = 'o', label='Y')
# axis[0, 1].set_title("vel")


# axis[1, 0].plot(packCounter, posY, color = 'g',  
#          marker = 'o', label='Y')
# axis[1, 0].set_title("Pos")
 
# axis[0, 0].set_xticks([0, 500, 1000, 1500, 2000])
# axis[0, 1].set_xticks([0, 500, 1000, 1500, 2000])
# axis[1, 0].set_xticks([0, 500, 1000, 1500, 2000])

plt.xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000])  
# plt.yticks([-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,-0.5,0,0.5,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])  
# plt.plot(packCounter, faccY, color = 'g',  
#          marker = 'o',label = "X") 
# plt.plot(packCounter, velY, color = 'r', 
#          marker = 'o',label = "Y") 
# plt.plot(packCounter, posY, color = 'b', 
#          marker = 'o',label = "Z") 
plt.plot(packCounter, faccX, color = 'g',  
         marker = 'o',label = "velX") 
plt.plot(packCounter, velX, color = 'r', 
         marker = 'o',label = "velX") 
plt.plot(packCounter, posX, color = 'b', 
         marker = 'o',label = "posX") 
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
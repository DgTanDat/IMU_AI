import csv 
import random

data = [
    ['timeStamp', 'facc', 'yaw', 'roll'],
]

def write_to_csv(filename, timestamp, facc, yaw, roll):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, facc, yaw, roll])

line_data = []

with open('university_records.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)


for i in range(0, 10):
    temp  = random.randint(0,10)
    write_to_csv('university_records.csv',temp, temp, temp, temp)



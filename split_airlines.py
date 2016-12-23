import csv

filename = "airlines/airlines"

cw = []
for i in range(14):
    cw.append(csv.writer(open(filename+str(i)+".csv","wb")))

cr = csv.reader(open("airlines.csv","rb"))

count = [0]*14

for row in cr:
    day = int(row[2])
    cw[day].writerow(row)
    count[day]+=1
    #print ("write",row,"to",day)

print count
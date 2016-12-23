#COMS cloud computing project
#Spark main function calculate SIR and flights
#Author: Bluester
#Teammate: Yimin Wei 	Jiachen Liu		Hongnin Yuan
#Version7
#Optimize runtime
#Flights only depart when people is enought
#With mortal rate

from pyspark import SparkContext, SparkConf
from kafka_manager import send_message
import time
import json
import sys

disease = {'alpha':0.6,'beta':0.1,'gamma':0.03} 		#alpha is the infect rate, beta is the recover rate, gamma death rate
startCondition = {'basyo':'US','ninzu':100000,'day':5}
loop = 10
time1=time.time()
total_time = 0
topic = 'plague-'									#topic of kafka

#take the arguements								#(10, ['0'										, '1'		  , '2' , '3', '4'  , '5'  , '6'  , '7'  , '8',  '9'])
print(len(sys.argv),sys.argv)						#(10, ['/home/hadoop/SparkLord/pycode/SIR_v6.py', 'session_id', 'RU', '5', '1.0', '0.4', '0.1', '0.0', '25', '9'])
if(len(sys.argv) == 10):
	topic = sys.argv[1]
	startCondition = {'basyo':sys.argv[2],'ninzu':int(sys.argv[3]),'day':int(sys.argv[9])}	
	disease = {'alpha':float(sys.argv[5]),'beta':float(sys.argv[6]),'gamma':float(sys.argv[7])} 
	loop = int(sys.argv[8])
print("topic",topic)
print("startCondition",startCondition)
print("disease",disease)
print("loop",loop)

#Initialize the population
def initialPop(line):   							#(country,[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])    
	tokens = line.split(',')
	if len(tokens) == 3:
		if tokens[0]==bstartCondition.value['basyo']:
			[SNo,INo,RNo,DNo] = [int(tokens[2])-bstartCondition.value['ninzu'],bstartCondition.value['ninzu'],0,0]
			TNo = SNo+INo+RNo+DNo
			[SRate,IRate,RRate,DRate] = [SNo*1.0/TNo,INo*1.0/TNo,RNo*1.0/TNo,DNo*1.0/TNo]
			return (tokens[0].encode('utf-8'),[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])
		else: 
			[SNo,INo,RNo,DNo] = [int(tokens[2]),0,0,0]
			[SRate,IRate,RRate,DRate] = [1.0,0.0,0.0,0.0]
			return (tokens[0].encode('utf-8'),[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])	
	else:
		return None

#Initialize the flights
def initialFlight(line):							#((dep, dest]), volume )
	tokens = line.split(',')
	if len(tokens) == 6 and tokens[4]!=tokens[5]:	# Departure != Destiny
		return ((tokens[4].encode('utf-8'),tokens[5].encode('utf-8')),int(tokens[1]))
	else:
		return None	

def SIRoneDay(line):											#Calculate SIR for each country
	[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate] = line[1]
	newInfect = int(SNo*INo*bdisease.value['alpha']/(SNo+INo+RNo+DNo))
	newInfect = min(SNo,newInfect)
	newRecover = int(INo*bdisease.value['beta'])
	newDead = int(INo*bdisease.value['gamma'])
	if newRecover!=0 or newDead!=0:
		newRecover = min(int(newRecover*1.0/(newDead+newRecover)*INo),newRecover)	
		newDead = min(int(newDead*1.0/(newDead+newRecover)*INo),newDead)	
	SNo -= newInfect
	INo += (newInfect-newRecover-newDead)
	RNo += newRecover      
	DNo += newDead
	TNo = SNo + INo + RNo + DNo
	[SRate,IRate,RRate,DRate] = [SNo*1.0/TNo,INo*1.0/TNo,RNo*1.0/TNo,DNo*1.0/TNo]
	return(line[0],[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])

def calculatePopOnFlight(line):						#Calculate the Number of S,I,R one each flight					
	dep = line[0]									
	dest = line[1][1][0]
	volume = line[1][1][1]
	[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate] = line[1][0]
	FSNo = int(volume*SRate)
	FINo = int(volume*IRate)
	FRNo = int(volume*RRate)
	return ((dep,dest),[FSNo,FINo,FRNo])			#((dep,dest),[FSNo,FINo,FRNo])


def sumTwoList(list1,list2):
	result = []
	for i in range(len(list1)):
		result.append(list1[i]+list2[i])
	return result

def departure(line):								#Country's population minus depart flights' population							
	if(line[1][1] is None):							#(dep, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], None))
		return (line[0],line[1][0])					#(country,[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])  
	else:											#(dep, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], [FSNo,FINo,FRNo]))
		[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate] = line[1][0]
		[FSNo,FINo,FRNo] = line[1][1]
		SNo -= FSNo
		INo -= FINo
		RNo -= FRNo
		return (line[0],[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate]) #(country,[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])  

def arrive(line):									#Country's population plus arrive flights' population			
	if(line[1][1] is None):							#(dep, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], None))
		return (line[0],line[1][0])					#(country,[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])  
	else:											#(dep, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], [FSNo,FINo,FRNo]))
		[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate] = line[1][0]
		[FSNo,FINo,FRNo] = line[1][1]
		SNo += FSNo
		INo += FINo
		RNo += FRNo
		return (line[0],[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate]) #(country,[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate])  


def sendToKafka(data,day):
	dict_msg = {}
	dict_pop = {}
	for line in data:
		#print line
		dict_pop[line[0]] = {"S":line[1][0],"I":line[1][1],"R":line[1][2],"D":line[1][3]}
	dict_msg["topic"] = topic
	dict_msg["day"] = day
	dict_msg["population"] = dict_pop
	json_msg = json.dumps(dict_msg)
	#send_message(json_msg,"world")
	send_message(json_msg,topic)
	#print json_msg

conf = SparkConf().setAppName('SIR').setMaster('local')
sc = SparkContext(conf=conf)

bdisease = sc.broadcast(disease) 			
bstartCondition = sc.broadcast(startCondition)


rawPopulation = sc.textFile('hdfs:///user/ds/countries.csv')
population = rawPopulation.map(lambda line:
    initialPop(line)
).filter(lambda line:
    line is not None
).coalesce(1)

#for line in mapPopulation.value:
#	print line,mapPopulation.value.get(line)


#Initial flights
flights=[]
for i in range(14):												
	flights.append(
		sc.textFile('hdfs:///user/ds/airlines/airlines'+str(i)+'.csv').map(lambda line:
			initialFlight(line)									#((dep,dest),volume) inorder to reduceByKey
		).filter(lambda line:
			line is not None
		).reduceByKey(lambda x,y:
			x+y
		).map(lambda line:			
			(line[0][0],(line[0][1],line[1]))
		).coalesce(1).cache()									#(dep,(dest,volume)) inorder to join with country
	)

total_outs = [] 												#Total departure people from one country
for i in range(14):	
	total_outs.append(
		flights[i].map(lambda line:
			(line[0],line[1][1])
		).reduceByKey(lambda x,y:
			x+y
		).coalesce(1).cache()
	)


time2 = time.time()
print("Initialize cost",time2-time1)
total_time += time2-time1
time1= time2


for i in range(loop):
	time1=time.time()
	print("loop",i)
	time3 = time.time()
#Calculate SIR for one day
	population = population.map(lambda line:
		SIRoneDay(line)												#Calculate SIR for each country
	).sortByKey().coalesce(1)
	time4 = time.time()
	print("SIR one day cost",time4-time3)
	time3 = time4
 	
 	sendToKafka(population.collect(),i+1)

	time4 = time.time()
	print("Send to Kafka cost",time4-time3)
	time3 = time4

#If the country do not have enough people to board on the flights, the country will be excluded from the departure
	day = (bstartCondition.value['day']+i+1)%14
	enough_country = population.join(							#country with enough people
		total_outs[day]
	).filter(lambda line:		
		line[1][0][0] + line[1][0][1] + line[1][0][2] > line[1][1]	#SNo + INo + RNo > sum of people on flights
	).map(lambda line:
		(line[0],line[1][0])
	).coalesce(1)

	time4 = time.time()
	print("Enought country cost",time4-time3)
	time3 = time4


	curflight = enough_country.join(									#(dep, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], (dest,volume)))
		flights[day]
	).map(lambda line:
		calculatePopOnFlight(line)
	).coalesce(1)																#((dep,dest)[FSNo,FINo,FRNo])

	time4 = time.time()
	print("Calculate flights cost",time4-time3)
	time3 = time4

	population = population.leftOuterJoin(							#Flights departure
		curflight.map(lambda line:									#(dep,[FSNo,FINo,FRNo])
			(line[0][0],line[1])
		).reduceByKey(lambda x,y:
			sumTwoList(x,y)
		).coalesce(1)															#(dep, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], [FSNo,FINo,FRNo])) || (dep, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], None))
	).map(lambda line:
		departure(line)
	).coalesce(1)																

	#(country,[SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate]) 
	#for line in population.collect(): 
	#	print line													 

	time4 = time.time()
	print("Flights departure cost",time4-time3)
	time3 = time4	

	population = population.leftOuterJoin(							#Flights arive
		curflight.map(lambda line:									#(dest,[FSNo,FINo,FRNo])
			(line[0][1],line[1])
		).reduceByKey(lambda x,y:
			sumTwoList(x,y)
		).coalesce(1)															#(dest, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], [FSNo,FINo,FRNo])) || (dest, ([SNo,INo,RNo,DNo,SRate,IRate,RRate,DRate], None))
	).map(lambda line:
		arrive(line)
	).coalesce(1)

	time4 = time.time()
	print("Flights arrive cost",time4-time3)
	time3 = time4	

	#curflight.unpersist()
	time2 = time.time() 
	print("loop",i+1,"cost",time2-time1)
	total_time += time2-time1
	time1=time2
	print

print("total cost",total_time)



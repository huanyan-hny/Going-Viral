from pyspark import SparkContext, SparkConf

def initialPop(line):       
   tokens = line.split(',')
   if len(tokens) == 2:
      return [tokens[0].encode('utf-8'),[int(tokens[1]),0,0]]      #[country,[S,I,R]]
   else:
      return None

def g(x):
	x[1][0]=100
	print x

#Initilize spark
conf = SparkConf().setAppName('test').setMaster('local')
sc = SparkContext(conf=conf)



rawPopulation = sc.textFile('hdfs:///user/ds/worldPopulation.csv')
population = rawPopulation.map(lambda line:
    initialPop(line)
).filter(lambda line:
    line is not None
).cache()

mapPOP = sc.broadcast(population.collectAsMap())


mapPOP.value.get('Turkmenistan')[1]=100
print mapPOP.value.get('Turkmenistan')[1]

for line in mapPOP.value:
	mapPOP.value.get(line) =[1000,1000,1000]
   	print line,mapPOP.value.get(line)
#population.foreach(g)

from concurrent.futures import ThreadPoolExecutor
import requests, os, sys, re, csv

data = file('flightData.txt')
country_populations = dict()
country_codes = dict()
populations = dict()
airports = dict()
airlines = dict()

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


def getAirlines():
	count=0
	for line in data:
		index1 = line.find(' ')
		index2 = find_nth(line,' ',2)
		index3 = index2+1
		while(not line[index3].isdigit()):
			index3 = index3+1
		index4 = line[:index3].rfind(',')
		index5 = find_nth(line[index3:],' ',2)+index3+1
		index6 = find_nth(line[index3:],' ',3)+index3
		index7 = line.rfind(',')
		index8 = line.rfind(' ')
		name = line[:index1]
		capacity = line[index1+1:index2]
		from_city = line[index2+1:index4]
		departure_time = line[index5:index6]
		to_city = line[index6+1:index7]
		arrival_time = line[index8+1:len(line)].strip('\n')
		if (to_city!=""):
			airlines[count]=[name,capacity,from_city,departure_time,to_city,arrival_time]
			count = count+1

baseurl = "http://192.168.0.7:8080/sim/add_airline?"

def executePush(i):
	formattedFromCity = airlines[i][2].replace(" ","+")
	formattedToCity = airlines[i][4].replace(" ","+")
	url = baseurl + "name=" + airlines[i][0] + "&capacity=" + airlines[i][1] + "&departure_time=" + airlines[i][3] + "&from_city=" + formattedFromCity + "&arrival_time=" + airlines[i][5] + "&to_city=" + formattedToCity
	response = requests.get(url)
	if response.status_code==200:
		print "Successfully pushed by url:", url
	else: 
		print response.status_code, "Failed to push url:", url
		with open('failedAirlines.txt','a') as f:
			f.write(url)


def pushAirlines():
	pool = ThreadPoolExecutor(20)
	for i in airlines:
		pool.submit(executePush,i)


getAirlines()
pushAirlines()











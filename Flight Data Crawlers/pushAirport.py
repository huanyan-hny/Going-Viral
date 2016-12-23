from concurrent.futures import ThreadPoolExecutor
import requests, os, sys, re, csv

data = file('flightData.txt')
country_populations = dict()
country_codes = dict()
populations = dict()
airports = dict()

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

sampleLine = "1553,\"Ciampino\",\"Rome\",\"Italy\",\"CIA\",\"LIRA\",41.799361,12.594936,427,1,\"E\",\"Europe/Rome\""

def match(city,country,line):
	items = line.split(",")
	if city == items[2].strip('"') and country == items[3].strip('"'):
		return True
	return False


def getLocation(city, country):
	icao_map = file('airport_mapping.txt')
	latitude = "0"
	longitude = "0"
	for line in icao_map:
		index1 = 5
		if match(city,country,line):
			while(not line[index1].isdigit()):
				index1 = index1 + 1
			if (line[index1-1]=='-'):
				index1 = index1 - 1
			index2 = line[index1:].find(',')+index1+1
			index3 = line[index2:].find(',')+index2
			latitude = line[index1:index2-1]
			longitude = line[index2:index3]
			if (country=="Sheffield"):
				country = "United Kingdom"
			if (country=="Netherlands Antilles"):
				country = "Netherlands"
			if (country=="Santiago Island"):
				country = "Cape Verde"
			return [country,latitude,longitude]
	return ["None","None","None"]

def getAirport():
	for line in data:
		if "Unknown" in line:
			continue
		index1 = find_nth(line,' ', 2)
		index2 = line.find(',')
		index3 = re.search('\d', line[index1:]).start()+index1-1
		city = line[index1+1:index2]
		country = line[index2+2:index3]
		if (city == "London"):
			print country
		if city not in airports:
			airports[city] = getLocation(city,country)
		index5 = find_nth(line,',',2)
		index4 = index5
		while not line[index4].isdigit():
			index4 = index4-1
		index6 = re.search('\d', line[index5:]).start()+index5-1
		city = line[index4+2:index5]
		country = line[index5+2:index6]
		if (city == "London"):
			print country
		if city not in airports:
			airports[city] = getLocation(city,country)

count = 0
failedAirports = []
baseurl = "http://192.168.0.7:8080/sim/add_airport?"
updateBaseurl = "http://192.168.0.7:8080/sim/update_airport_location?"

def executePush(city):
	global count
	global failedAirports
	formattedCity = city.replace(" ","+")
	formattedCountry = airports[city][0].replace(" ","+")
	url = baseurl + "city_name=" + formattedCity + "&country_name=" + formattedCountry + "&latitude=" + airports[city][1] + "&longitude=" + airports[city][2]
	response = requests.get(url)
	if response.status_code==200:
		print "Successfully pushed by url:", url
		count = count+1
	else: 
		failedAirports.append(city)
		print response.status_code, "Failed to push url:", url

def pushAirport():
	pool = ThreadPoolExecutor(8)
	for city in airports:
		pool.submit(executePush,city)
	print "Pushed " + str(count) + " Airports"
	for fail in failedAirports:
		print fail

def updatePush(city):
	global count
	global failedAirports
	formattedCity = city.replace(" ","+")
	formattedCountry = airports[city][0].replace(" ","+")
	url = updateBaseurl + "city_name=" + formattedCity + "&latitude=" + airports[city][1] + "&longitude=" + airports[city][2]
	response = requests.get(url)
	if response.status_code==200:
		print "Successfully updated by url:", url
		count = count+1
		with open('UpdatedAirports.txt','a') as f:
			f.write(url)
	else: 
		failedAirports.append(city)
		print response.status_code, "Failed to update url:", url
		with open('failedAirports.txt','a') as f:
			f.write(url)

def pushAirport():
	pool = ThreadPoolExecutor(8)
	for city in airports:
		pool.submit(updatePush,city)
	print "Updated " + str(count) + " Airports"
	for fail in failedAirports:
		print fail

getAirport()
pushAirport()
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


def getPopulation():
	with open('population.csv', mode = 'rU') as inFile:
		reader = csv.reader(inFile)
		for rows in reader:
			populations[rows[0].strip()] = rows[1].strip()

def getCountryPopulations():
	for line in data:
		if "Unknown" in line:
			continue
		index1 = line.find(',')+2
		index2 = re.search('\d', line[index1:]).start()+index1-1
		country = line[index1:index2]
		if country not in country_populations:
			country_populations[country] = populations.get(country,0)
		index3 = find_nth(line, ',', 2)+2
		index4 = re.search('\d', line[index3:]).start()+index3-1
		country = line[index3:index4] 
		if country not in country_populations:
			country_populations[country] = populations.get(country,0)
	country_populations.pop("Sheffield") #United Kingdom
	country_populations.pop("Netherlands Antilles") #Netherlands
	country_populations.pop("Santiago Island") #Cape Verde


def getCountryCodes():
	for key in country_populations:
		codes = file('countryCodes.txt')
		found = False
		for line in codes:
			if key == line[:line.find(',')]:
				found = True
				country_codes[key] = line[line.rfind(',')+1:len(line)].strip('\n')
				country_codes[key].strip('\t')
				break
		if not found:
			country_codes[key] = "None"

def pushCountry():
	count = 0
	baseurl = "http://192.168.0.7:8080/sim/add_country?"
	for key in country_populations:
		formattedKey = key.replace(" ","+")
		url = baseurl + "name=" + formattedKey + "&population=" + country_populations[key] + "&code=" + country_codes[key]
		response = requests.get(url)
		if response.status_code==200:
			print "Successfully pushed by url:", url	
			count = count+1		
		else: 
			if response.status_code!=500:
				print "Failed to push url:", url			
	print "Pushed " + str(count) + " countries"

getPopulation()
getCountryPopulations()
getCountryCodes()
pushCountry()
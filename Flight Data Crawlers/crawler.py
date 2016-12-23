#! /usr/bin/env python
#coding:utf-8
from __future__ import print_function
import os, requests, sys, bs4, pytz, datetime, time

reload(sys)
sys.setdefaultencoding('utf-8')

weekday_departure = "unset"
date_departure = datetime.date.today()
one_day = datetime.timedelta(days=1)

def getCityAndCountry(airport_code):
	time.sleep(0.5)
	icao_map = file('../icao.txt')
	airport_code = str(airport_code)
	for line in icao_map:
		if airport_code in line:
			groups = line.split(',')
			icao_map.close
			return groups[2][1:len(groups[2])-1] + ", " + groups[3][1:len(groups[3])-1]
	icao_map.close
	return "Unknown"

def getNumberOfPassenger(plane_type):
	return {
		'B73': 150,
		'B74': 500,
		'B76': 250,
		'B77': 400,
		'B78': 250,
		'A30': 250,
		'A31': 160,
		'A32': 150,
		'A34': 250,
		'A35': 300,
		'A38': 750,
		'E13': 35,
		'E14': 45,
		'E45': 50,
		'E17': 80,
		'E19': 100,
		'DC1': 310,
		'DH8': 50,
		'CRJ': 90,
		'F2T': 10,
		'MD1': 300,
		'MD8': 150,
	}.get(plane_type, 200)



def weekdayIndex(weekday):
	return {
		'Mon': 1,
		'Tue': 2,
		'Wed': 3,
		'Thu': 4,
		'Fri': 5,
		'Sat': 6,
		'Sun': 7
	}.get(weekday,0)

def getDepartureTime(time):
	global weekday_departure
	global date_departure
	weekday = time[:3]
	if (weekday_departure!=weekday):
		weekday_departure = weekday
		date_departure = date_departure - one_day
	hour = time [4:6]
	minute = time[7:9]
	time_departure = datetime.time(int(hour),int(minute),0)
	dt_departure = datetime.datetime.combine(date_departure,time_departure)
	return dt_departure

def getArrivalTime(time):
	weekday = time[:3]
	diff = weekdayIndex(weekday)-weekdayIndex(weekday_departure)
	date_arrival = date_departure
	if (diff==-6 or diff>0):
		date_arrival = date_departure + one_day

	if (diff<0 or diff==6):
		weekday_arrival = weekday
		date_arrival = date_departure - one_day

	hour = time [4:6]
	minute = time[7:9]
	time_arrival = datetime.time(int(hour),int(minute),0)
	dt_arrival = datetime.datetime.combine(date_arrival,time_arrival)
	return dt_arrival

def setInitialDate(time):
	global weekday_departure
	weekday_departure = time[:3]

def craw(response, airport_name):
	base = getCityAndCountry(airport_name)
	f = open('/home/ubuntu/' + airport_name, 'ab')
	soup = bs4.BeautifulSoup(response.text, "html.parser")
	flights = soup.select('a[href^="/live/flight/id"]')
	if (len(flights)):
		setInitialDate(flights[0].parent.parent.next_sibling.next_sibling.next_sibling.contents[0])
	for i in range(0,len(flights)):
		plane_no = flights[i].contents[0] if len(flights[i].contents) else "???"
		plane_type = flights[i].parent.parent.next_sibling.contents[0].contents[0].contents[0] if len(flights[i].parent.parent.next_sibling.contents[0].contents[0].contents) else "Unknown"
		airport_code = flights[i].parent.parent.next_sibling.next_sibling.contents[2].contents[0]
		departure_time = flights[i].parent.parent.next_sibling.next_sibling.next_sibling.contents[0]
		departure_time_zone = flights[i].parent.parent.next_sibling.next_sibling.next_sibling.contents[1].contents[0]
		arrival_time = flights[i].parent.parent.next_sibling.next_sibling.next_sibling.next_sibling.contents[0]
		arrival_time_zone = flights[i].parent.parent.next_sibling.next_sibling.next_sibling.next_sibling.contents[1].contents[0] 
		print (plane_no, getNumberOfPassenger(plane_type[:3]), base, getDepartureTime(departure_time), getDepartureTime(departure_time).strftime("%s"), getCityAndCountry(airport_code[-4:]),getArrivalTime(arrival_time), getArrivalTime(arrival_time).strftime("%s"), file = f)
		print (plane_no, getNumberOfPassenger(plane_type[:3]), base, getDepartureTime(departure_time), getDepartureTime(departure_time).strftime("%s"), getCityAndCountry(airport_code[-4:]),getArrivalTime(arrival_time), getArrivalTime(arrival_time).strftime("%s"))
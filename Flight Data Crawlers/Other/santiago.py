#! /usr/bin/env python
#coding:utf-8
from __future__ import print_function
import os, requests, sys, bs4, pytz, datetime, time, crawler

reload(sys)
sys.setdefaultencoding('utf-8')

airport_name = "SCEL"
offset = 0

postData = {
	'referer':"https://zh.flightaware.com/account/session",
	'mode':"login",
	'flightaware_username':"TroyYuan",
	'flightaware_password':"flightforcloud"
}

s = requests.session()
s.post(url='https://zh.flightaware.com/account/session', data = postData)

def main():
	global offset
	global flight_url
	for i in range(1,300):
		flight_url = "http://flightaware.com/live/airport/" + airport_name + "/departures?;offset=" + str(offset) + ";order=actualdeparturetime;sort=DESC"
		crawler.craw(s.get(flight_url), airport_name)
		print("Finished offset" + str(offset))
		offset+=40

main()
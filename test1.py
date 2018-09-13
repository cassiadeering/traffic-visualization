from selenium import webdriver #need a virtual browser to instantiate the search, in order to get height of divs
import re #regex to search for digits
import time #need to pause/sleep while webdriver searches
from bs4 import BeautifulSoup #BeautifulSoup is what parses the html
import codecs #for file writing
import string #to manipulate strings
from googleplaces import GooglePlaces, types, lang #googleplaces api
import json #work with json objects - store data in a file in json format

#json data object
data = {}

#with google places api,
#can do 100 text searches in a 24 hour period for free with each key.
#the nearby search can do 100x more than text searches in a 24 hour period
PLACES_API_KEY = "AIzaSyCxfuFaoxIgRisdI_FvpY8kvtBMt5z-ZaQ"
google_places = GooglePlaces(PLACES_API_KEY)

#if we want user input from the command line, uncomment the next 2 lines. 
#user_input = raw_input("Please enter the brand name and location (what you would search in Google, e.g. starbucks king and university waterloo): ")
#print "You entered:", user_input

#if raw input uncommented, comment the following line.
user_input = "Starbucks 247 King Waterloo"
query_result = google_places.text_search(query=string.replace(user_input, " ", "+"))
#if query_result.has_attributions:
	#print query_result.html_attributions

for place in query_result.places:
	data["name"] = place.name

	#each store has a unique id, we don't want to store the same information twice
	data["id"] = place.place_id
	#data['location'] = place.geo_location
	#print data
	#print place.name
	#print place.geo_location
	#print place.place_id

	#need to call an additional details function to get the below options
	place.get_details()
	data["address"] = place.details[u"formatted_address"]
	data["duration_of_visit"] = []
	data["schedule"] = {}
	#print place.website
	#print place.url
	#print place.local_phone_number

	#instantiate webdriver
	driver = webdriver.Chrome()
	url = "https://www.google.ca/search?q=" + data["name"] + " " + data["address"] 
	driver.get(url)
	time.sleep(1)
	content = driver.page_source.encode("utf-8").strip()

	#store data in a parseable format
	soup = BeautifulSoup(content, "html.parser")

	#write data to a file
	file_write = codecs.open("output_" + data["name"] + " " + data["address"] + ".txt", "wb", "utf8")
	i = 0

	def find_typical_duration():
		#this is what the div is called for the typical duration data
		d = soup.findAll("div", attrs={"class": "_B1k"})
		counter = 0
		for e in d: 
			for f in e: 
				if counter is not 0: #don't need the "Plan your visit: " part, the first part of the data
					data["duration_of_visit"].append(str(f))
				counter = counter + 1
				
	def find_histogram_data(day):
		global i
		i = 0 

		# finding data in html, with the specific div classes Google uses
		histogram_data = []
		histogram_data.append(soup.findAll("div", attrs={"aria-label": "Histogram showing popular times on " + day}))
		if (histogram_data[0]): 
			heights_sun = histogram_data[0][0].findAll("div", attrs={"class": "lubh-bar"})
			live_time_sun = histogram_data[0][0].findAll("div", attrs={"class": "lubh-bar lubh-sel"})
			times = histogram_data[0][0].findAll("div", attrs={"class": "_ipj"})
			new_times = histogram_data[0][0].findAll("div", attrs={"class": "_epj"})
			
			time_arr = []

			# 24 hour time makes it far easier for the JavaScript file, 
			# so it is necessary to strip the a/p from Google's times.
			# Also, Google only has text every 3 hours. 
			# 6a, 9a, 12p etc. 
			# In order for the JavaScript file to properly read these arrays, 
			# interpolation is needed, to populate the hours in between,
			# as well as converting to 24 hour format.
			for time in new_times:
				count = 0
				c = ""
				for hour in time: 
					if "a" in hour.text:
						hour_stripped = int(hour.text.strip("a"))
						#print str(hour_stripped) + " first"
						if hour_stripped == 12:
							hour_stripped = hour_stripped - 12
							#print str(hour_stripped) + " seconds"
						else:
							hour_stripped = hour_stripped
						#print "end of first loop"
						time_arr.append(hour_stripped)
						count = count + 1
					elif "p" in hour.text:
						hour_stripped = int(hour.text.strip("p"))
						if hour_stripped == 12: 
							hour_stripped = hour_stripped
							#print str(hour_stripped) + " third"
						else: 
							hour_stripped = hour_stripped + 12
							#print str(hour_stripped) + " fourth"
						#print str(hour_stripped) + "end of 2nd loop"
						#print str(hour_stripped) + " last version? "
						time_arr.append(hour_stripped)
						count = count + 1
					else: #blank time
						if count is not 0:
							#print str(time_arr[count-1] + 1) + " last else"
							time_arr.append(time_arr[count-1] + 1)
							count = count + 1

			recordsSun = []
			for table in heights_sun:
				table_style = table.get("style")
				#print table_style
				recordsSun.append(table_style)
			recordsSunLive = []
			for table in live_time_sun:
				table_style = table.get("style")
				recordsSunLive.append(table_style)
			for record in recordsSunLive:
				print "recordsSunLive: " + record # this still includes background colour
			#compiling this first makes it faster
			re_digit = re.compile("\d")
			#print>>file_write, day + ": "
			#i = 0

			#split off any extra information we don't need 
			for element in recordsSun:
				parts = element.split(";")
				#print parts
				for part in parts:
					new_part = part.strip("height :px")
					#print new_part
					if (bool(re_digit.search(new_part)) and not "#" in new_part): #don't want anything that's a colour
						part_percentage = float(new_part) / 76 * 100 #76px is the height of the div, according to the CSS
						#print>>file_write, part_percentage
						#print "i: " + str(i)
						#print "length: " + str(len(time_arr))
						if (i < len(time_arr)):
							data["schedule"][day].update({time_arr[i]: part_percentage})
							#print str(time_arr[i]) + ": " + str(part_percentage)
						i = i + 1

			# this next section can be included if live times are available
			# for element in recordsSunLive:
			# 	parts = element.split(";")
			# 	for part in parts:
			# 		new_part = part.strip("height: px")
			# 		if (bool(re_digit.search(new_part))):
			# 			part_percentage = float(new_part) / 76 * 100
			# 			print part_percentage
		else: 
			print "Popular times data does not exist for " + data["name"] + " at " + data["address"] + " on " + day + "."
			#data["schedule"][day].append("Popular times data does not exist for " + data['name'] + " at " + data['address'] + " on " + day + ".")

	#initialize all the json arrays required for each day of the week,
	#then call them
	data["schedule"]["Sundays"] = {}
	find_histogram_data("Sundays")
	data["schedule"]["Mondays"] = {}
	find_histogram_data("Mondays")
	data["schedule"]["Tuesdays"] = {}
	find_histogram_data("Tuesdays")
	data["schedule"]["Wednesdays"] = {}
	find_histogram_data("Wednesdays")
	data["schedule"]["Thursdays"] = {}
	find_histogram_data("Thursdays")
	data["schedule"]["Fridays"] = {}
	find_histogram_data("Fridays")
	data["schedule"]["Saturdays"] = {}
	find_histogram_data("Saturdays")

	find_typical_duration()

	#json load data is the opposite of data dumps
	json_data = json.dumps(data)
	print>>file_write, json_data
	file_write.close()
	#print data["duration_of_visit"]
	print data["address"]
driver.quit()

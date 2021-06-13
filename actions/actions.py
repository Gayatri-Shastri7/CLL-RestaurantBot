# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import logging
import requests
import json
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import random


logger = logging.getLogger(__name__)


ZOMATO_API_KEY = 'dc4f13f34b2754f1b044d01e36008001'
API_URL = 'https://developers.zomato.com/api/v2.1/'
HEADERS = {
'User-agent': 'curl/7.43.0', 
'Accept': 'application/json',
'user_key': ZOMATO_API_KEY
}

class  ActionFindRestaurants(Action):
	def name(self):
	
		return 'action_find_restaurants'

	def parse_search(self, restaurants):
		data = {
			'name' : [],
			'cuisines' : [],
			'rating' : [],
		}

		for rest in restaurants:
			rt = rest['restaurant']
			data['name'].append(rt['name'])
			data['cuisines'].append(rt['cuisines'])
			data['rating'].append(rt['user_rating']['aggregate_rating'])

		return data

	def get_location(self, location):

		url = "https://developers.zomato.com/api/v2.1/locations?query="+str(location)

		payload={}
		headers = {
		'user-key': 'dc4f13f34b2754f1b044d01e36008001',
		'Cookie': 'csrf=4fe404a8e04ecdedf9c0a3ecc681f0ad; fbcity=3; fbtrack=89760581a99470a8f0746645d60a5fbb; zl=en; AWSALBTG=ceUB8gA8aVZ2+feeppN5/gMIMpVrsODT3beOP1n7jeBLraKX6TQZicz3slUH147hu06t0y/hCTWTKiZxJrLAWq0JE+opY6MKa0wJueCiLNGjtcbY9HDWioywm0lITkb1/y4Kb5K4HBxkEevvHFchAJjJbIOWDOHuLRcipUkouGG0Mvyj7VE=; AWSALBTGCORS=ceUB8gA8aVZ2+feeppN5/gMIMpVrsODT3beOP1n7jeBLraKX6TQZicz3slUH147hu06t0y/hCTWTKiZxJrLAWq0JE+opY6MKa0wJueCiLNGjtcbY9HDWioywm0lITkb1/y4Kb5K4HBxkEevvHFchAJjJbIOWDOHuLRcipUkouGG0Mvyj7VE='
		}

		res = requests.request("GET", url, headers=headers, data=payload)

		latitude = 28.625789
		longitude = 77.210276

		if res.status_code == 200:
			latitude = res.json()['location_suggestions'][0]['latitude']
			longitude = res.json()['location_suggestions'][0]['longitude']

		return str(latitude), str(longitude)

	def run(self, dispatcher, tracker, domain):

		location = tracker.get_slot('location') 
		cuisine = tracker.get_slot('cuisine') 

		dispatcher.utter_message(location+cuisine)

		latitude, longitude = self.get_location(location)
		url = 'https://developers.zomato.com/api/v2.1/' + 'search?q=' + cuisine + '&lat=' +latitude+ '&lon=' + longitude + '&sort=rating'
		payload={}
		headers = {
		'user-key': 'dc4f13f34b2754f1b044d01e36008001',
		'Cookie': 'csrf=d00b76e48661ec0f06d04ba4a42da770; fbcity=3; fbtrack=89760581a99470a8f0746645d60a5fbb; zl=en; AWSALBTG=tE5wx6DJU1zoxIql1RLb+KB67CVEyv/ToMWINXbHWvkbdWZeFq4HFgkzr7m/aTwtCrJrgzOqH6+0MOBlE7W0T/X8ZRtbt3pcWJNXFIW3eBTqPhRapwvOTm8UKZEu/5gQzuMofN3qj4iB5sVpqzJCj7R4qG8lPZQBGa83nHDQPd7Ba3bUGHQ=; AWSALBTGCORS=tE5wx6DJU1zoxIql1RLb+KB67CVEyv/ToMWINXbHWvkbdWZeFq4HFgkzr7m/aTwtCrJrgzOqH6+0MOBlE7W0T/X8ZRtbt3pcWJNXFIW3eBTqPhRapwvOTm8UKZEu/5gQzuMofN3qj4iB5sVpqzJCj7R4qG8lPZQBGa83nHDQPd7Ba3bUGHQ='
		}

		res = requests.request("GET", url, headers=headers, data=payload)
		if res.status_code == 200:
			restaurants = self.parse_search(res.json()['restaurants'])
			out_greet_msg = '*Here are top  results for {} in {}*'.format(cuisine, location)
			dispatcher.utter_message(out_greet_msg)
			print(len(restaurants))

			if len(restaurants) > 0:
				output = []
				for idx, rest in enumerate(restaurants):
					out_st = 'Restaurant: '+restaurants['name'][idx]+'\nCuisines: '+restaurants['cuisines'][idx]+'\nRating: '+restaurants['rating'][idx]+'\n'
					output.append(out_st)
					dispatcher.utter_message(out_st)

				output = '\n'.join(output)
			else:
				dispatcher.utter_message('No Restaurant found :( Please try again!')
		else:
			dispatcher.utter_message('FAILED.')
		
		return []

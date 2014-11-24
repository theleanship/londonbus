#!/usr/bin/python
from pymongo import MongoClient
from pycurl import Curl
from cStringIO import StringIO
from urllib import urlencode
from bson.json_util import loads, dumps
import web
import sys


urls = ( 
	'/', 'index',
	'/route/(.*)', 'routes',
	'/stop', 'stops',
	'/bus', 'buses',
	'/updateroute', 'updateRoute',
	'/pass', 'passThrough'
)

app = web.application(urls, globals())
mongo = MongoClient()
db = mongo.tubewatch

class index:
	""" A placeholder API response
	"""
	def GET(self):

		web.header('Access-Control-Allow-Origin',      '*')
		return 'API stuff in here'

class routes:
	""" Get a JSON object full of London bus route information,
		includes a list of stops on each route.
	"""
	def GET(self, number):

		web.header('Access-Control-Allow-Origin',      '*')
		
		# TODO, return full stop object for all routes
		if not number:
			routes = db.routes.find({}, { "route": 1 })
			numbers = []
			for route in routes:
				numbers.append(route['route'])

		else:
			numbers = number.split(',')

		routes = []

		print 'compiling routes'

		for n in numbers:

			route = db.routes.find_one({'route': n })

			if route:

				for run in route['runs']:
					run['Stops'] = db.stops.find({ 
							"StopId": { "$in": run['Stops'] } 
						},
						{
							"StopCode": 1,
							"StopId": 1,
							"Latitude": 1,
							"Longitude": 1
						});

				routes.append(route)

		print 'dumping'

		return dumps(routes)

class stops:
	def GET(self):

		web.header('Access-Control-Allow-Origin',      '*')
		stops = db.stops.find({},{ "Longitude": 1, "Latitude": 1 }, limit=20000)
		return dumps(stops)

class updateRoute:
	def GET(self, response):
		web.header('Access-Control-Allow-Origin',      '*')
		# print loads(response)["runs"]["encodedPoints"]
		print "HELLO"
		return dumps({ "Stupid": "You're suppost to post"})

	def POST(self):
		web.header('Access-Control-Allow-Origin',      '*')
		route = loads(web.data())

		for run, runObject in enumerate(route['runs']):
			db.routes.update({"route": route['route'] }, 
				{
					"$set": { 
						"runs." + str(run) + ".distances": runObject["distances"], 
						"runs." + str(run) + ".points": runObject["points"], 
						"runs." + str(run) + ".encodedPathWithStops": runObject["encodedPathWithStops"]
					}
				}
			)

		print route['route']
		return dumps({ "hello": "bonjour"})

class buses:
	def GET(self):
		blob = []
		example = { "id": 5678, "Latitude": -0.33399444, "Longitude": 54.00944433, "Bearing": 180 }

		for n in range(1,7000):
			blob.append(example)
		# buses = db.buses.find({}, { "Registration": 1 })
		return dumps(blob)

class passThrough:
	def GET(self):
		web.header('Access-Control-Allow-Origin',      '*')
		getInput = web.input()
		return self.callAPI(getInput)

	def callAPI(self,params={}):

		# pull data
		buf = StringIO()

		curl = Curl()

		url = params.url.__str__()
		del params.url

		curl.setopt(curl.URL, url + '?' + urlencode(params))
		curl.setopt(curl.WRITEFUNCTION, buf.write)

		try:
			curl.perform()
		except error:
			print 'Failed on curl'
		response = buf.getvalue()
		buf.close()
		return response



if __name__ == "__main__": 
	app.run()
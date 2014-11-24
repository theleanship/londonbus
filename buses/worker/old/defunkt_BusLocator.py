from pymongo import MongoClient
from pycurl import Curl
from cStringIO import StringIO
from urllib import urlencode
from json import loads
from Bus import Bus
import time


class BusLocator:

	db = None
	buses = {}

	def __init__(self):
		mongo = MongoClient()
		self.db = mongo.tubewatch

		busData = self.db.buses.find({}, { "Registration": 1 })
		routeData = self.db.routes.find()

		busesLoaded = self.loadBuses(busData)

		print busesLoaded
		self.locate()


	def loadBuses(self, busData):

		for bus in busData:
			self.buses[bus['Registration']] = Bus(self.db, bus['Registration'])

		return True

	def locate(self):
		for bus in self.buses:
			self.buses[bus].getLocation()

b = BusLocator()

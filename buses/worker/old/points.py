# Updates all routes with new point sturcture
# and adds distances in points

from pymongo import MongoClient
from pycurl import Curl
from cStringIO import StringIO
from urllib import urlencode
from json import loads
from math import sin, cos, sqrt, atan2, radians

class Points:

    db = None

    def getDistanceFromLatLonInKm(self,lat1,lon1,lat2,lon2):

        R = 6371 # Radius of the earth in km
        dLat = radians(lat2-lat1)  # deg2rad below
        dLon = radians(lon2-lon1)

        a1 = sin(dLat/2) * sin(dLat/2)
        a2 = cos(radians(lat1)) * cos(radians(lat2))
        a3 = sin(dLon/2) * sin(dLon/2)
        a = a1+a2*a3
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c # Distance in km

        return d

    def route(self):
        routes = self.db.routes.find()

        for route in routes:

            for run in route['runs']:
                lastX = None
                lastY = None
                lastD = 0
                print run
                for i, point in enumerate(run['points']):

                    try:
                        if(i>0):
                            distance = self.getDistanceFromLatLonInKm(lastX, lastY, point['kb'], point['jb'])
                            lastD = distance+lastD
                            print lastD
                        lastX = point['kb']
                        lastY = point['jb']

                        run['points'][i] = {
                            "latitude": point['jb'],
                            "longitude": point['kb'],
                            "distance": lastD
                        }
                    except KeyError:
                        break

                try:
                    del run['distances']
                except KeyError:
                    continue

            self.db.routes.update({"route": route['route'] }, { "$set": { "runs": route['runs'] } })
            print route['route'], 'updated'

    def __init__(self):
        # get DB
        mongo = MongoClient()
        self.db = mongo.tubewatch

        self.route()

p = Points()

# x1 = -0.11947
# y1 = 51.58229000000001
# x2 = -0.11956199999997352
# y2 = 51.582142


# distance = sqrt( ((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1)) )

# for x in range(0, 101):
# 	dX = (x2-x1)*(x/float(100))
# 	dY = (y2-y1)*(x/float(100))
# 	print x,dX,dY, x1+dX, y1+dY

# print distance

from pymongo import MongoClient
from pycurl import Curl
from cStringIO import StringIO
from urllib import urlencode
from json import loads


class Bus:

    db = None

    def callAPI(self, url, params={}):

        # pull data
        buf = StringIO()

        curl = Curl()
        curl.setopt(curl.URL, url + '?' + urlencode(params))
        curl.setopt(curl.WRITEFUNCTION, buf.write)

        try:
            curl.perform()
        except:
            print 'Failed on all routes curl'

        response = buf.getvalue()
        buf.close()
        return response

    def routeList(self):
        allRoutes = loads(self.callAPI('http://www.tfl.gov.uk/tfl/gettingaround/maps/buses/tfl-bus-map/dotnet/AllRoutes.aspx'))

        return allRoutes['AllRoutes']

    def storeStop(self, stop):
        existing = self.db.stops.find_one({"StopId": stop['StopId']})

        if(existing==None):
            self.db.stops.insert(stop)

        return stop

    def storeRoute(self, number, route, stops, run):

        routeInfo = None

        # pull route info
        for r in route['Routes']:
            if r['Route'] == number:
                routeInfo = r

        # check if exists
        existing = self.db.routes.find_one({"route": number})

        if existing is not None and (run == 2):
            existing["runs"].append({
                        "From": routeInfo['From'],
                        "Towards": routeInfo['Towards'],
                        "encodedLevels": routeInfo['encodedLevels'],
                        "encodedPoints": routeInfo['encodedPoints'],
                        "Color": routeInfo['Color'],
                        "StartPoint": {
                            "Latitude": routeInfo["startPoint"]['Latitude'],
                            "Longitude": routeInfo["startPoint"]['Longitude'],
                        },
                        "EndPoint": {
                            "Latitude": routeInfo["endPoint"]['Latitude'],
                            "Longitude": routeInfo["endPoint"]['Longitude'],
                        },
                        "Stops": stops
                    })
            self.db.routes.update({ "route": number }, { "$set": { "runs": existing["runs"] } })

        # doesn't exist, and routeinfo does
        if not existing and routeInfo:
            self.db.routes.insert(
                { 
                    "route": number, 
                    "runs": [{
                        "From": routeInfo['From'],
                        "Towards": routeInfo['Towards'],
                        "encodedLevels": routeInfo['encodedLevels'],
                        "encodedPoints": routeInfo['encodedPoints'],
                        "Color": routeInfo['Color'],
                        "StartPoint": {
                            "Latitude": routeInfo["startPoint"]['Latitude'],
                            "Longitude": routeInfo["startPoint"]['Longitude'],
                        },
                        "EndPoint": {
                            "Latitude": routeInfo["endPoint"]['Latitude'],
                            "Longitude": routeInfo["endPoint"]['Longitude'],
                        },
                        "Stops": stops
                    }]
                }
            )

        return number

    def storeRoutes(self, numbers):

        for n in numbers:
            stops = []

            # run 1
            try:
                route = loads(self.callAPI(
                    'http://www.tfl.gov.uk/tfl/gettingaround/maps/buses/tfl-bus-map/dotnet/FullRoute.aspx',
                    {'route': n, 'run': 1}
                ))
            except ValueError:
                print 'Failed on ' + n

            for stop in route['Stops']:
                self.storeStop(stop)
                stops.append(stop['StopId'])

            self.storeRoute(n, route, stops, 1)

            # do run 2
            stops = []

            try:
                route = loads(self.callAPI(
                    'http://www.tfl.gov.uk/tfl/gettingaround/maps/buses/tfl-bus-map/dotnet/FullRoute.aspx',
                    {'route': n, 'run': 2}
                ))
            except ValueError:
                print 'Failed on ' + n

            for stop in route['Stops']:
                self.storeStop(stop)
                stops.append(stop['StopId'])

            if len(route['Stops']) > 0:
                self.storeRoute(n, route, stops, 2)

            print 'stored' + n

    def __init__(self):
        # get DB
        mongo = MongoClient()
        self.db = mongo.tubewatch

        routeNumbers = self.routeList()
        self.storeRoutes(routeNumbers)


b = Bus()
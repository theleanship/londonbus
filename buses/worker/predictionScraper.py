import settings
from pymongo import MongoClient
from pycurl import Curl
from cStringIO import StringIO
from urllib import urlencode
from json import loads
from Bus import Bus
import time


db = None
server = None
buses = {}
routes = {}
stops = {}
predictor = None

# Predictor
# Scrapes the TFL API for predictions
#
class PredictionScraper:

    def callAPI(self,url, params={}):

        # pull data
        buf = StringIO()

        curl = Curl()
        curl.setopt(curl.URL, url + '?' + urlencode(params))
        curl.setopt(curl.WRITEFUNCTION, buf.write)

        try:
            curl.perform()
        except Error:
            print 'Failed on all routes curl'

        response = buf.getvalue()
        buf.close()
        return response

    def parsePredictions(self):

        time_start = time.time()

        response = self.callAPI('http://countdown.api.tfl.gov.uk/interfaces/ura/instant_V1',
            {
                'ReturnList': 'StopID,LineID,DirectionID,VehicleID,TripID,RegistrationNumber,EstimatedTime'
            }
        )

        json = loads('{ \"response\": [' + response.replace('\r\n', ',') + '] }')

        print 'Got json'
        print time.time()-time_start, 'seconds'

        # group prediction adding for faster DB

        for i, bus in enumerate(json['response']):

            if i == 0: continue

            try:
                buses[bus[5]].addPrediction( bus[1], bus[2], bus[3], bus[5], bus[7] )

            except (KeyError, IndexError):
                buses[bus[5]] = Bus(db, { "BusID": bus[4], "Registration": bus[6], "Trips": [] }, True) # NEW bus
                buses[bus[5]].addPrediction( bus[1], bus[2], bus[3], bus[5], bus[7] )

        print 'Predictor: inserted predictions'
        print time.time()-time_start, 'seconds'

        for bus in buses:
            buses[bus].save()


        print 'Predictor: saved buses'
        print time.time()-time_start, 'seconds'

        time.sleep(30)
        self.parsePredictions()

    def __init__(self):
        print "predictor: Init"
        print "Predictor: Calling TFL"
        self.parsePredictions()

def getBuses():
    for bus in db.buses.find({}):
        buses[bus["BusID"]] = Bus(db,bus)

    print 'Got the buses'

def getStops():
    for stop in db.stops.find({}):
        stops[stop["StopId"]] = stop

    print 'Got the stops'

def getRoutes():

    for route in db.routes.find():
        routes[route["route"]] = route

    print 'Got the routes'


def main():

    global server, mongo, db, buses, routes, locator, predictor
    # get DB
    mongo = MongoClient()
    db = mongo.tubewatch

    getBuses()
    getStops()
    getRoutes()

    predictor = PredictionScraper()


if __name__ == "__main__":
    main()
import settings
from pymongo import MongoClient
import math
from Bus import Bus
import time
import threading
from gevent import monkey; monkey.patch_all()
import gevent
from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace

db = None
server = None
buses = {}
routes = {}
stops = {}
locator = None

# Locator
# Calculates locations of buses on their routes according to predictions
#
class BusLocator(threading.Thread):

    db = None
    buses = {}

    def __init__(self):
        threading.Thread.__init__(self)

        print "Locator: Init"

    def run(self):
        print "Locator: Thread started, Pulling buses"
        self.locateBuses()

    def loadBuses(self, busData):

        for bus in busData:
            buses[bus['Registration']] = Bus(self.db, bus['Registration'])

        return True

    def pointDistance(self, route, run, code):

        lng = None
        lat = None

        try:
            for stop in routes[route]["runs"][run]["Stops"]:
                if stops[stop]["StopCode"] == code:
                    lng = stops[stop]["Longitude"]
                    lat = stops[stop]["Latitude"]

            # Not found
            if lng is None:
                return None

            for point in routes[route]["runs"][run]["points"]:
                if abs(point["longitude"]-lng) < 0.000001:
                    if point["latitude"] == lat:
                        return point["distance"]

            # Not found...

            return None
        except (KeyError, IndexError):
            # Not found...
#            print 'Index error, run not found'
            return None

    def distanceBetweenStops(self, prediction):
        s1Distance = self.pointDistance(prediction["route"], prediction["run"], prediction["s1"]["code"])
        s2Distance = self.pointDistance(prediction["route"], prediction["run"], prediction["s2"]["code"])

        if s1Distance is None or s2Distance is None:
            return None

        return s1Distance+((s2Distance-s1Distance)*prediction["progress"])

    def locate(self, route, run, distance):

        # Get point arriving at next
        for i, point in enumerate(routes[route]["runs"][run]["points"]):
            if not distance>point["distance"]:
                next = i
                break;

        # last point departed
        last = next-1
        lPoint = routes[route]["runs"][run]["points"][last]
        nPoint = routes[route]["runs"][run]["points"][next]

        R = 6371
        dLat = math.radians(nPoint["latitude"]-lPoint["latitude"])
        dLon = math.radians(nPoint["longitude"]-lPoint["longitude"])
        lat1 = math.radians(lPoint["latitude"])
        lat2 = math.radians(nPoint["latitude"])
        lon1 = math.radians(lPoint["longitude"])

        a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2);
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c

        y = math.sin(dLon) * math.cos(nPoint["latitude"])
        x = math.cos(lPoint["latitude"])*math.sin(nPoint["latitude"]) - math.sin(lPoint["latitude"])*math.cos(nPoint["latitude"])*math.cos(dLon)
        brng = math.atan2(y, x)

        lat2 =  math.asin( math.sin(lat1)*math.cos(d/R) +
                           math.cos(lat1)*math.sin(d/R)*math.cos(brng) )

        lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
                    math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

        print R, d, dLon, brng, lPoint["latitude"], lPoint["longitude"], lat2, lon2

#        print (nPoint['latitude']-lPoint['latitude']) * distance-lPoint["distance"]

        return { "latitude": lat2, "longitude": lon2 }

#        return { "latitude": lPoint["latitude"]+((nPoint["latitude"]-lPoint["latitude"])*distance), "longitude": lPoint["longitude"]+((nPoint["longitude"]-lPoint["longitude"])*distance) }

    def locateBuses(self):

        print "Locator: locating buses"

        count = 0

        for bus in buses:
            trip = buses[bus].getCurrentTrip()
            if trip is None:
                continue
            if trip["line"]=="91" or trip["line"]==91:
                print "found 91 bus"

        for bus in buses:

            prediction = buses[bus].getLocation() # return stop1, stop1.arrives, stop2, stop2.arrives

            if prediction is not None:
#                print prediction["route"], "91"
                if prediction["route"]!="91":
                    continue

                if prediction["progress"] is not None:
                    distance = self.distanceBetweenStops(prediction)

                    if distance is not None:
                        for stop in routes[prediction["route"]]["runs"][prediction["run"]]["Stops"]:
                            if stops[stop]["StopCode"] == prediction["s2"]["code"]:
                                lng = stops[stop]["Longitude"]
                                lat = stops[stop]["Latitude"]

                        location = self.locate(prediction["route"], prediction["run"], distance)
                        count = count+1
#                        r_server.delete(bus)
#                        r_server.lpush(bus, location["longitude"], location["latitude"], bus) #reversed indexs as adds from bottom
#                        broadcastLocation(server, '/locations', 'location', { "id": bus, "coord": { "latitude": lat, "longitude": lng } })
                        broadcastLocation(server, '/locations', 'location', { "id": bus, "coord": location })
                else:
                    pass

        print "buses located", count
        time.sleep(3)
        self.locateBuses()

# Frontend server
class Front(object):
    def __init__(self):
        self.buffer = []

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/') or 'index.html'

        if path.startswith('static/') or path == 'index.html':
            try:
                data = open(path).read()
            except Exception:
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'/locations': BaseNamespace})
        else:
            return not_found(start_response)

def broadcastLocation(server, namespace, eventname, location):

    pkt = dict(type="event",
        name=eventname,
        args=location,
        endpoint=namespace)

#    try:
    if server is not None:
        for sessid, socket in server.sockets.iteritems():
            socket.send_packet(pkt)
            print 'sent packet', pkt

def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']

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

    locator = BusLocator()
    locator.start()

    server = SocketIOServer(('0.0.0.0', 8080), Front(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843))
#    gevent.spawn()
    server.serve_forever()


if __name__ == "__main__":
    main()


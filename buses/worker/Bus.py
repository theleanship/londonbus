from time import mktime as mktime
from datetime import datetime
import math

class Bus:
    BusID = None
    Registration = None

    def __init__(self, db, obj, new=False):
        self.db = db
        self.BusID = obj["BusID"]
        self.Registration = obj["Registration"]
        self.Trips = obj["Trips"]
        self.add_jess_to_the_github_bus()

        if new:
            self.save()
            
    def add_jess_to_the_github_bus(self):
        print "YOU CAN'T KEEP ME OUT GRAEME!"
        self.jess_is_on_the_github_bus = True

    def save(self):
        existing = self.db.buses.find_one({ 'BusID': self.BusID })

        if existing is None:
            self.db.buses.insert({
                "BusID": self.BusID,
                "Registration": self.Registration,
                "Trips": self.Trips
            })
        else:
            self.db.buses.update(
                { "BusID": self.BusID },
                {
                    "$set": {
                        "Trips": self.Trips
                    }
                }
            )

    def addPrediction(self, stopID, line, direction, tripID, time):

        existing = self.getTrip(tripID)

        if existing is None:
            self.Trips.append({
                "tripID": tripID,
                "line": line,
                "direction": direction,
                "predictions": [[stopID, datetime.fromtimestamp(int(time/1000))]]
            })

        else:
            # update existing prediction or add new
            found = False

            for prediction in existing["predictions"]:
                if prediction[0]==stopID:
                    found = True
                    prediction[1] = datetime.fromtimestamp(int(time/1000))

            if not found:
                existing["predictions"].append([stopID, datetime.fromtimestamp(int(time/1000))])


    def getTrip(self, tripID):

        for trip in self.Trips:

            if trip['tripID']==tripID:
                return trip

        return None

    def nextTrip(self, curTrip=0):
        next = None

        for trip in self.Trips:
            
            if trip["tripID"] > curTrip:

                if next is None:
                    next = trip["tripID"]

                if trip["tripID"] < next:
                    next = trip["tripID"]

        return next

    def isTripFinished(self, tripID):

        trip = self.getTrip(tripID)

        if trip is not None:
            for prediction in trip["predictions"]:
                if prediction[1] > datetime.now():
                    return False

        # No upcoming arrivals, trip is finished
        return True


    def getCurrentTrip(self):
        current = 0

        while current is not None:
            current = self.nextTrip(current)

            if not self.isTripFinished(current):
                return self.getTrip(current)

        return None

    def getLocation(self):

        # Get current Trip
        currentTrip = self.getCurrentTrip()

        # Timings
        now = datetime.now()
        next = None
        last = None

        # Bus is not active, return None
        if currentTrip is None:
            return None

        # Find next and last
        for prediction in currentTrip["predictions"]:

            # find next visited stop
            if prediction[1] > now:

                if next is None:
                    next = prediction
                else:
                    if prediction[1] < next[1]:
                        next = prediction

            #  find last visited stop
            if prediction[1] < now:

                if last is None:
                    last = prediction
                else:
                    if prediction[1] > last[1]:
                        last = prediction

        # prediction object to be returned
        prediction = {
            "s1": None,
            "s2": None,
            "progress": None,
            "run": currentTrip["direction"]-1,
            "route": currentTrip["line"],
            "registration": self.Registration
        }

        # populate prediction
        if last is not None:
            prediction["s1"] = { "time": mktime(last[1].timetuple()), "code": last[0] }

        if next is not None:
            prediction["s2"] = { "time": mktime(next[1].timetuple()), "code": next[0] }

        if next and last is not None:
            prediction["progress"] =  (mktime(now.timetuple())-prediction["s1"]["time"]) / (prediction["s2"]["time"]-prediction["s1"]["time"])

        return prediction


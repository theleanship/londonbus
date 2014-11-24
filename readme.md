London Buses
============

I once attempted to create the first real time London bus map using the TFL prediction API. There are a couple of scripts in here that are kind of useful.

This is a bit of a dump of code I didn't want to lose but can't entirely remember what it does! Roughly putting it back together below. You will need python to run the scripts that scrape the APIs, the predictionScraper should run indefinetly constantly updating mongoDB with new predictions. At some point locaitons were being placed in redis before being broadcast for the frontend app to pick up - i'm not sure if this still exits.

This is all super hacky, good luck if you continue. Do as you wish with anything in this repo.

`buses/worker/stopScraper.py`
This scrapes an undocumented API used by TFLs live maps (might not work anymore!) and identifies all stops in the TFL network and works out the routes they are on. It will store all routes and their stops in mongoDB.

`buses/worker/predictionScraper.py`
Runs through the TFL bus arrival prediction api

`buses/node/locator.js`
Somewhere within this is some logic which finds a bus, works out where it was last seen and where it is due to arrive next. Based on the time difference it will plot the buses estimated location between those 2 points on a route and then render that on a google map. It will broadcast bus points via socket io which can be picked up by the frontend app.

`buses/worker.py`
A refactor of the scrapers above which run indefintly updating mongodb with real time data.

`map/`
Contains the code that renders the map
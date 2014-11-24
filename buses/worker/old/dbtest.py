from pymongo import MongoClient

c = MongoClient()

db = c.tubewatch

disruptions = db.disruptions

disruption = {
	'type': 1, 	
	'id': 'BNK',
	'found': 0, 
	'removed': 0,
	'source': 1,
}

disruptions.insert(disruption)

print disruptions.find_one({"id": "BNK"})
import redis
from json import dumps

r_server = redis.from_url('redis://localhost:6379')

for n in range(1,7000):
	r_server.lpush(n, -0.130303, 54.959595, "N91", 180)


print "Pushed", r_server.dbsize, "buses"

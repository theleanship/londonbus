var http = require("http"),
    url = require("url"),
    path = require("path"),
    fs = require("fs");

var app = http.createServer(function(request, response) {
 
  var uri = url.parse(request.url).pathname
    , filename = path.join(process.cwd(), uri);
  
  path.exists(filename, function(exists) {
    if(!exists) {
      response.writeHead(404, {"Content-Type": "text/plain"});
      response.write("404 Not Found\n");
      response.end();
      return;
    }
 
    if (fs.statSync(filename).isDirectory()) filename += '/index.html';
 
    fs.readFile(filename, "binary", function(err, file) {
      if(err) {        
        response.writeHead(500, {"Content-Type": "text/plain"});
        response.write(err + "\n");
        response.end();
        return;
      }
 
      response.writeHead(200);
      response.write(file, "binary");
      response.end();
    });
  });
}).listen(8002);


function postBuses() {
  buses = [];

  client.keys('*', function (err, keys) {
    // if (err) return console.log(err);

    for (key in keys) {
        thisKey = keys[key];
        client.lrange([thisKey, 0, 2], function(err, data) {
          console.log(data)
          buses.push({
            "id": data[0],
            "Latitude": data[1],
            "Longitude": data[2],
          })
        });
    }


    ready = function() {
      if(buses.length==keys.length) {
        io.sockets.emit('news', buses);
      } else {
        setTimeout(ready, 250);
      }
    }
   
    setTimeout(ready, 250);
    
  });
}

var io = require('socket.io').listen(app)
  , fs = require('fs')
  , redis = require("redis")
  , client = redis.createClient();

setInterval(postBuses, 1000);

io.sockets.on('connection', function (socket) {
  io.sockets.emit('news', { will: 'be received by everyone'});
});
var mapWidth = 1500;
var mapHeight = 900;
var offsetX = 747;
var offsetY = 197.3;

function get2DPoint(lat, lon) {

	// get x value
	x = (mapWidth*(180+lon)/360)%(mapWidth+(mapWidth/2));

	// convert from degrees to radians
	latRad = lat*Math.PI/180;

	// get y value
	mercN = Math.log(Math.tan((Math.PI/4)+(latRad/2)));
	y     = (mapHeight/2)-(mapWidth*mercN/(2*Math.PI));

	// return { x: x, y: y }
	return { x: (x-offsetX)*250, y: (y-offsetY)*250 }
}

buses = {};

function initialize() {
	var mapOptions = {
	  center: new google.maps.LatLng(51.51825,-0.128231),
	  zoom: 14,
	  mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	
	map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);

	var socket = io.connect('http://localhost');
		socket.on('news', function (data) {

		for(coord in data) {

			if(typeof buses[data[coord].id] === "undefined") {
				buses[data[coord].id] = new google.maps.Marker({
					position: new google.maps.LatLng(data[coord].Latitude, data[coord].Longitude),
					icon: 'bus.png',
					map: map,
				});
			} else {
				buses[data[coord].id].setPosition(new google.maps.LatLng(data[coord].Latitude, data[coord].Longitude))
			}
		}
	});
}



$(document).ready(function() {

	google.maps.event.addDomListener(window, 'load', initialize);

	// var canvas = document.getElementById("map");
	// canvas.width = mapWidth;
	// canvas.height = mapHeight;
	// var context = canvas.getContext("2d");

	// // context.fillStyle = "rgba(0,200,0, " + 0.6 + ")";
	// // $.ajax({
	// // 	url: "http://127.0.0.1:2001/stop",
	// // 	dataType: "json",
	// // 	async: false,
	// // 	success: function(data) {
	// // 		for(point in data) {
	// // 			point2d = get2DPoint(data[point].Latitude, data[point].Longitude);
	// // 			context.fillRect(point2d.x, point2d.y, 1,1);
	// // 		}
	// // 	}
	// // });

	// context.fillStyle = "rgba(204,0,0, " + 0.6 + ")";


});
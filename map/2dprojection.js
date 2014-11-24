var mapWidth = 1500;
var mapHeight = 900;
var offsetX = 747;
var offsetY = 197.3;

function get2DPoint(lon, lat) {

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

$(document).ready(function() {

	var canvas = document.getElementById("map");
	canvas.width = mapWidth;
	canvas.height = mapHeight;
	var context = canvas.getContext("2d");

	context.fillStyle = "rgba(204,0,0, " + 0.6 + ")";

	$.ajax({
		url: "http://127.0.0.1:2001/stop",
		dataType: "json",
		success: function(data) {
			for(point in data) {
				point2d = get2DPoint(data[point].Longitude, data[point].Latitude);
				// console.log(point2d)
				context.fillRect(point2d.x, point2d.y, 1,1);
			}
		}
	})
});
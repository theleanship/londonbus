// // var Bus = function() {
// // 	this.iteration = 0;
// // 	this.route = "009";
// // 	this.stops = [
// // 		{
// // 			id: 00000,
// // 			arrival: 000000000
// // 		}
// // 	];

// // 	this.purge = function() {
// // 		now = Date.now();
// // 		for arrivals < now:
// // 			del;
// // 	}

// // 	this.relevantStops = function() {

// // 		return lastStop, nextStop
// // 	}

// // 	this.update = function() {
// // 		stops = this.relevantStops();

// // 		locate(this.route, stops.last, stops.next);

// // 		iteration++;
// // 	}

// // }

// function locate(route, last, next) {
// 	// bus has left last
// 	// bus arrives at next at next.arrival
// 	// locate bus on route path
// }

$(document).ready(function() {

	var socket = io.connect('http://localhost');
		socket.on('news', function (data) {
		console.log(data);
		socket.emit('my other event', { my: 'data' });
	});
});
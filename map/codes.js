var map;

function initialize() {
	var mapOptions = {
	  center: new google.maps.LatLng(51.51825,-0.128231),
	  zoom: 14,
	  mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	
	map = new google.maps.Map(document.getElementById("map-canvas"),
	    mapOptions);
}

function getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2) {

  var R = 6371; // Radius of the earth in km
  var dLat = deg2rad(lat2-lat1);  // deg2rad below
  var dLon = deg2rad(lon2-lon1); 
  var a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
    ; 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  var d = R * c; // Distance in km
  return d;
}

function deg2rad(deg) {
  return deg * (Math.PI/180)
}

paths = [];
points = [];
distances = [];

function compare(a,b) {
  if (a.distance < b.distance)
     return -1;
  if (a.distance > b.distance)
    return 1;
  return 0;
}

function getPointByIndex(points, index) {
	for( point in points) {
		if(parseInt(points[point].idx)==index) return points[point];
	}

	return false;
}

function addToPath(path, lat, lon) {
		distances = [];
		shortest1 = null;
		shortest2 = null;

		for(set in path) {

			distance = getDistanceFromLatLonInKm(
					path[set].lat(), 
					path[set].lng(),
					lat, lon
				);
		
			distances.push({ "distance": distance, "idx": set, "lat": path[set].lat(), "lon": path[set].lng() });
			distances.sort(compare);
		}
		// console.log(distances);

		// 
		// CHECK direction going forwards
		//
			// console.log('GOING BACKWARDS');
			point1 = distances[0];
			point2 = distances[1];

			// order indices
			if(point1.idx<point2.idx) {
				point1 = distances[1];
				point2 = distances[0];
			} 

			checkDistance = true;
			i = 0;

			while(checkDistance && i < 10) {
				fromPoint2ToX = getDistanceFromLatLonInKm(point2.lat, point2.lon, lat, lon);
				fromPoint2ToPoint1 = getDistanceFromLatLonInKm(point2.lat, point2.lon, point1.lat, point1.lon);

				if(fromPoint2ToX>fromPoint2ToPoint1 ) {

					p1 = parseInt(point1.idx)-1;
					p2 = p1-1;
					// console.log(p1,p2);

					point1 = getPointByIndex(distances, p1);
					point2 = getPointByIndex(distances, p2);

					// console.log(point1, point2, fromPoint2ToX, fromPoint2ToPoint1, fromPoint2ToX>fromPoint2ToPoint1);
						

					if(!point1) break;
					if(!point1) break

					i = i+1;
					checkDistance = true;

				} else {
					checkDistance = false;
				}
			}

		//
		// CHECK direction going backwards
		//
		if(i==10) {
			// console.log('going forwards');
			point1 = distances[0];
			point2 = distances[1];

			// order indices
			if(point1.idx>point2.idx) {
				point1 = distances[1];
				point2 = distances[0];
			} 

			checkDistance = true;
			i = 0;

			while(checkDistance && i < 10) {
				fromPoint1ToX = getDistanceFromLatLonInKm(point1.lat, point1.lon, lat, lon);
				fromPoint1ToPoint2 = getDistanceFromLatLonInKm(point1.lat, point1.lon, point2.lat, point2.lon);

				if(fromPoint1ToX>fromPoint1ToPoint2 ) {

					p1 = parseInt(point1.idx)+1;
					p2 = p1+1;
					// console.log(p1,p2);

					point1 = getPointByIndex(distances, p1);
					point2 = getPointByIndex(distances, p2);
					
					// console.log(point1, point2, fromPoint1ToX, fromPoint1ToPoint2, fromPoint1ToX>fromPoint1ToPoint2);
					

					if(!point1) break;
					if(!point1) break

					i = i+1;
					checkDistance = true;

				} else {
					checkDistance = false;
				}
			}
		}

		// // splice into array
		if(parseInt(point1.idx)<parseInt(point2.idx)) spliceAt = point1.idx;
		else spliceAt = point2.idx;
		spliceAt = parseInt(spliceAt)+1;

		path.splice(spliceAt,0, new google.maps.LatLng(lat, lon))
		// console.log(i, point1.idx, point2.idx, spliceAt, lat, lon);
		return path;

}

function closestPoint(path, lat, lon) {
		
		shortest1 = null;
		shortest2 = null;

		for(set in path) {

			distance = getDistanceFromLatLonInKm(
					path[set].jb, 
					path[set].kb,
					lat, lon
				);

			if(shortest1==null) shortest1 = { "index": set, "distance": distance, "path": path[set] };

			if(shortest2==null || distance<shortest2.distance) {
				if(distance<shortest1.distance) {
					shortest2 = shortest1;
					shortest1 = { "index": set, "distance": distance, "path": path[set] };
				} else {
					shortest2 = { "index": set, "distance": distance, "path": path[set] };
				}
			}
		}
		
		return shortest1;
}

function distanceToStop(path, lat, lng) {
	total = 0;

	for(point in path) {
		if(point==0) continue;
		// console.log(lat, path[point].lat(), lng, path[point].lng());

		if(path[point-1].lat().toFixed(6)==lat.toFixed(6) && path[point-1].lng().toFixed(6)==lng.toFixed(6)) break;
		if(path[point].lat().toFixed(6)==lat.toFixed(6) && path[point].lng().toFixed(6)==lng.toFixed(6)) break;
		total = total+getDistanceFromLatLonInKm(path[point-1].lat(), path[point-1].lng(),path[point].lat(), path[point].lng());
	}

	return total;
}

function getRoute(number) {

	if(typeof number=="undefined") number = '';

	$.getJSON("http://127.0.0.1:2001/route/" + number, function(data) {
		// console.log(data)

		for(route in data) {
			console.log(data[route]);
			// insert markers
			for(run in data[route]['runs']) {
				var coords = [];

				var decodedPath = google.maps.geometry.encoding.decodePath(data[route]['runs'][run].encodedPoints);

				for(stop in data[route]['runs'][run]['Stops']) {
					points.push({ "lat": data[route]['runs'][run]['Stops'][stop].Latitude, "longi": data[route]['runs'][run]['Stops'][stop].Longitude });
					console.log(data[route]['runs'][run]['Stops'][stop]);
					decodedPath = addToPath(
						decodedPath,
						data[route]['runs'][run]['Stops'][stop].Latitude, 
						data[route]['runs'][run]['Stops'][stop].Longitude
					);

					data[route]['runs'][run]['Stops'][stop].distance = distanceToStop(
						decodedPath,
						data[route]['runs'][run]['Stops'][stop].Latitude, 
						data[route]['runs'][run]['Stops'][stop].Longitude
					);

					// console.log(distance);

					var marker = new google.maps.Marker({
						position: new google.maps.LatLng(data[route]['runs'][run]['Stops'][stop].Latitude, data[route]['runs'][run]['Stops'][stop].Longitude),
						icon: 'bus.png',
						map: map,
						title: data[route]['runs'][run]['Stops'][stop].StopName,
						StopCode: data[route]['runs'][run]['Stops'][stop].StopCode
					});

					google.maps.event.addListener(marker, 'click', function() {
						updateInfo(this);
					});
				}

				// insert paths
				var path = new google.maps.Polyline({
					path: decodedPath,
					strokeColor: "#FF0000",
					strokeOpacity: 1.0,
					strokeWeight: 2
				});

				data[route]['runs'][run].encodedPathWithStops = google.maps.geometry.encoding.encodePath(path.getPath());

				path.setMap(map);
			}
			// updateRoute(route["route"], data[route]['runs']);
		}

	});
}

function updateInfo(marker) {

	$.ajax({
		url: "http://127.0.0.1:2001/pass", 
		type: "GET",
		data: { 
			"url": "http://countdown.api.tfl.gov.uk/interfaces/ura/instant_V1",
			"StopID": marker.StopCode,
			"ReturnList": "VehicleID,RegistrationNumber,LineName,DestinationText,EstimatedTime,ExpireTime" 

		},
		dataType: "json",
		dataFilter: function(data, type) {

			data = data.replace(/\n/g, ',');
			data = '[' + data + ']';
			// console.log('pre', data);
			return data;
		},
		success: function(data) {
			showPredictions(data);
		},
		error: function(data) {
			// console.log('error', data);
		}
	});

	$('#where').html(marker.title);
}

function updateRoute(route, runs) {

	$.ajax({
		url: "http://127.0.0.1:2001/updateroute", 
		data: JSON.stringify({ 
			"route": route,
			"runs": runs,

		}),
		type: "POST",
		// contentType : 'application/json',
		dataType: "text",
		success: function(data) {
			// console.log('i posted');
		},
		error: function(data) {
			// console.log('error', data);
		}
	});
}

function showPredictions(predictions) {
	var text = "";
	for(var i=1; i<predictions.length; i++) {
		time = predictions[i][5]-new Date();
		minutes = time/60000;

		console.log(predictions[i][1] + ' ' + predictions[i][2] + ' ' + minutes + 'm' );
	}
}


$(document).ready(function() {
	google.maps.event.addDomListener(window, 'load', initialize);

	getRoute('8,98,10,101,120');
});
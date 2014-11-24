buses = {};

function initialize() {

    WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf";
    WEB_SOCKET_DEBUG = true;

    var mapOptions = {
        center: new google.maps.LatLng(51.51825,-0.128231),
        zoom: 14,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);

    var socket = io.connect('/locations');
    socket.on('location', function (data) {

        if(typeof buses[data.id] === "undefined") {
            buses[data.id] = new google.maps.Marker({
                position: new google.maps.LatLng(data.coord.latitude, data.coord.longitude),
                icon: '/static/bus.png',
                map: map
            });
        } else {
            buses[data.id].setPosition(new google.maps.LatLng(data.coord.latitude, data.coord.longitude))
        }
    });
}



$(document).ready(function() {

    google.maps.event.addDomListener(window, 'load', initialize);

});

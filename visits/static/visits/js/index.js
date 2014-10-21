var map;
(function ($, L, Foundation) {

    var iconOnline,
        iconOffline,
        markers;

    if (L) {
        iconOnline = L.AwesomeMarkers.icon({
            markerColor: 'red',
            icon: 'coffee'
        });
        iconOffline = L.AwesomeMarkers.icon({
            markerColor: 'blue'
        });
    }

    function reloadActiveUsers() {
        $.ajax('?').done(function (data) {
            if (data) {
                $('.subheader').text(data.subheader);
                if (data.dayVisits) $('.dayVisits').empty().append(data.dayVisits);
                if (data.visitorLocations) $('.visitorLocations').empty().append(data.visitorLocations);
                if (data.points && map) {
                    if (markers) markers.forEach(map.removeLayer);
                    markers = data.points.map(function (point) {
                        return L.marker([point[0], point[1]], {
                            icon: point[2] ? iconOnline : iconOffline,
                            clickable: false,
                            zIndexOffset: point[2] ? 10 : 5
                        }).addTo(map);
                    });
                }
            }
            console.log('DATA', data);
        });
        //$('.subheader').load('reload');
        setTimeout(reloadActiveUsers, 60000);
    }
    $(reloadActiveUsers);

    $(function () {
        if (Foundation) {
            $(document).foundation();
        }
        if ($('#map').length && L) {
            map = L.map('map', {
                zoomControl: false // .setView([0, 0], 2)
            }).fitBounds([[-35, -45], [65, 45]]);
            map.touchZoom.disable();
            map.doubleClickZoom.disable();
            map.scrollWheelZoom.disable();
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
        }
    });

}(jQuery, window.L, window.Foundation));

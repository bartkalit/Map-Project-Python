var map
var markers = [];
var directionsService;
var directionsRenderer;

function initMap() {
    var updateFunc = window.updateMapFunc;
    var myLatLng = {lat: 37.7749, lng: -122.4194};  // Set the initial coordinates here
    map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 12
    });
    
    var form = document.getElementById('input-form');
    var input_userid = document.getElementById('input-userid');
    var input_lat1;
    var input_lng1;
    var input_lat2;
    var input_lng2;

    if (updateFunc == "travel-plan-update") {
        input_lat1 = document.getElementById('input-lat1');
        input_lng1 = document.getElementById('input-lng1');
        input_lat2 = document.getElementById('input-lat2');
        input_lng2 = document.getElementById('input-lng2');
    }
    
    form.addEventListener('submit', async e => {
        e.preventDefault();
        
        var userId = input_userid.value;
        var location1;
        var location2;
        var result;

        if (updateFunc == "travel-plan-update") {
            location1 = [input_lat1.value, input_lng1.value];
            location2 = [input_lat2.value, input_lng2.value];
            const response = await fetch(updateFunc, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    userId: userId,
                    location1: location1,
                    location2: location2
                })
            })
            result = await response.json();
        }
        else {
            const response = await fetch(updateFunc, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    userId: userId
                })
            })
            result = await response.json();
        }
        const locations = JSON.parse(result.locations);
        
        map.setCenter(locations[0]);

        clearMarkers();
        fillTable(locations);

        if (updateFunc == "hop-time-update") {
            fillFriendsTable(result.friends, result.chosen_f);
        }
        if (updateFunc == "travel-plan-update") {
            clearDirections();
            directionsService = new google.maps.DirectionsService();
            directionsRenderer = new google.maps.DirectionsRenderer();
            directionsRenderer.setMap(map);
            var origin = locations[0];
            var destination = locations[locations.length - 1];
            var waypoints = [];
            for (var i = 1; i <  locations.length - 1; i++) {
                waypoints.push({'location': locations[i]})
            }
            var request = {
                'origin': origin,
                'destination': destination,
                'waypoints': waypoints,
                'travelMode': google.maps.TravelMode.DRIVING 
            }
            directionsService.route(request, function(result, status) {
                if (status == google.maps.DirectionsStatus.OK) {
                    directionsRenderer.setDirections(result);
                }
            });
        } else {
            addMarkers(locations)
        }
    });
}

function clearDirections() {
    if (directionsRenderer != null){
        directionsRenderer.setMap(null);
        directionsRenderer = null;
    }
}

function clearMarkers() {
    markers.forEach(marker => {
        marker.setMap(null);
    });
    markers = [];
}

function addMarkers(locations) {
    for(var i = 0; i < locations.length; i++){
        var marker = new google.maps.Marker({
            position: locations[i],
            label: i && i.toString(),
            map: map,
            title: 'Location ' + i.toString()
        });

        if(i === 0) {
            marker.setIcon('http://maps.google.com/mapfiles/kml/pal5/icon13.png');
        }

        markers.push(marker);
    }
}

function clearTable(tableBody) {
    while (tableBody.firstChild) {
        tableBody.removeChild(tableBody.firstChild);
    }
}

function fillTable(locations) {
    var tableBody = document.querySelector('#locationTable tbody');
    clearTable(tableBody)
    var counter = 0;
    locations.forEach(loc => {
        var row = document.createElement('tr');
        addColumn(row, counter);
        addColumn(row, loc.user_id);
        addColumn(row, loc.lat);
        addColumn(row, loc.lng);
        addLocationId(row, loc.location_id);
        addColumn(row, loc.duration, 0, "time");
        tableBody.appendChild(row);
        counter++;
    });
    tableBody.firstChild.classList.add("is-selected");
}

function fillFriendsTable(locations, chosen_f) {
    var tableBody = document.querySelector('#friendTable tbody');
    clearTable(tableBody)
    locations.forEach(userId => {
        var row = document.createElement('tr');
        addColumn(row, userId);
        if (chosen_f.includes(userId)) {
            row.classList.add("is-selected");
        }
        tableBody.appendChild(row);
    });
}

function addColumn(row, column_data, fixed = null, text="") {
    var cell = document.createElement('td');
    if(column_data !== null) {
        if (text === "time") {
            if (column_data >= 100) {
                m = parseInt(column_data / 60);
                s = column_data % 60;
                cell.textContent = m + "m " + s.toFixed(fixed) + "s";
            }
            else {
                cell.textContent = column_data.toFixed(fixed) + "s";
            }
        }
        else if(fixed !== null) {
            cell.textContent = column_data.toFixed(fixed);
        }
        else {
            cell.textContent = column_data;
        }
    }
    row.appendChild(cell);
}

function addLocationId(row, column_data) {
    var cell = document.createElement('td');
    if(column_data !== null) {
        if (column_data === -1) 
            cell.textContent = "START";
        else if (column_data === -2)
            cell.textContent = "END";
        else
            cell.textContent = column_data;
    }
    row.appendChild(cell);
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
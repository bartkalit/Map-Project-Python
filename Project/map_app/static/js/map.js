var map
var markers = [];

function initMap() {
    var myLatLng = {lat: 37.7749, lng: -122.4194};  // Set the initial coordinates here
    map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 10
    });
    
    var form = document.getElementById('input-form');
    var input = document.getElementById('input-userid');

    form.addEventListener('submit', async e => {
        e.preventDefault();

        var userId = input.value;
        
        const response = await fetch('travel-time-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ userId: userId })
        })
        const result = await response.json();
        const locations = JSON.parse(result.locations)
        
        map.setCenter(locations[0])

        clearMarkers()
        addMarkers(locations)
        fillTable(locations)
    });
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
            map: map,
            title: 'Location ' + i.toString()
        });

        if(i) {
            marker.setIcon('http://maps.google.com/mapfiles/ms/icons/blue-dot.png');
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

    locations.forEach(loc => {
        var lat = loc.lat;
        var lng = loc.lng;
        var row = document.createElement('tr');
        
        var latCell = document.createElement('td');
        latCell.textContent = lat.toFixed(2);
        row.appendChild(latCell);

        var lngCell = document.createElement('td');
        lngCell.textContent = lng.toFixed(2);
        row.appendChild(lngCell);

        tableBody.appendChild(row);
    });
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
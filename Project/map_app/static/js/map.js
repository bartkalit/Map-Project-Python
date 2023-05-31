var map
var markers = [];

function initMap() {
    var myLatLng = {lat: 37.7749, lng: -122.4194};  // Set the initial coordinates here
    map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 12
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
        addColumn(row, loc.location_id);
        addColumn(row, loc.duration, 0, "time");
        tableBody.appendChild(row);
        counter++;
    });
    tableBody.firstChild.classList.add("is-selected");
}

function addColumn(row, column_data, fixed = null, text="") {
    var cell = document.createElement('td');
    console.log(column_data)
    if(column_data !== null) {
        if (text === "time") {
            if (column_data >= 100) {
                m = parseInt(column_data / 60);
                s = column_data % 60;
                cell.textContent = m + "m " + s + "s";
            }
            else {
                cell.textContent = column_data + "s";
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
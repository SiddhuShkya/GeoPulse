
let map;
let drawnItems = new L.FeatureGroup();
let currentGeoJSON = null;
let currentTileLayer = null;

// Initialize map
function initMap() {
    map = L.map('map').setView([28.7221, 80.6362], 7);

    currentTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add drawing controls
    const drawControl = new L.Control.Draw({
        draw: {
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false,
            polygon: {
                allowIntersection: false,
                showArea: true
            }
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });

    map.addControl(drawControl);
    map.addLayer(drawnItems);

    // Handle drawing events
    map.on(L.Draw.Event.CREATED, function (e) {
        const layer = e.layer;
        drawnItems.clearLayers();
        drawnItems.addLayer(layer);
        updateGeoJSON();
    });

    map.on(L.Draw.Event.EDITED, function (e) {
        updateGeoJSON();
    });

    map.on(L.Draw.Event.DELETED, function (e) {
        currentGeoJSON = null;
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('viewGeoJSONBtn').disabled = true;
    });
}

// Change map type
// Change map type
// Change map type
function changeMapType(type) {
    console.log('Changing map type to:', type);
    const mapType = type || 'Default';

    if (!map) {
        console.error('Map not initialized');
        return;
    }

    // Remove current tile layer
    if (currentTileLayer) {
        map.removeLayer(currentTileLayer);
    }

    if (mapType === 'Satellite') {
        currentTileLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Esri World Imagery'
        }).addTo(map);
    } else {
        currentTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }

    // Re-add drawn items (ensure they are on top)
    if (drawnItems.getLayers().length > 0) {
        drawnItems.bringToFront();
    }
}

// Search location
async function searchLocation() {
    const locationName = document.getElementById('locationSearch').value;
    if (!locationName) {
        showAlert('Please enter a location name', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/search_location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ location: locationName })
        });

        const data = await response.json();

        if (response.ok) {
            const lat = data.lat;
            const lon = data.lon;

            document.getElementById('latitude').value = lat.toFixed(6);
            document.getElementById('longitude').value = lon.toFixed(6);

            map.setView([lat, lon], 12);
            L.marker([lat, lon]).addTo(map)
                .bindPopup(`📍 ${locationName} <br>${lat.toFixed(6)}, ${lon.toFixed(6)}`)
                .openPopup();
        } else {
            showAlert(data.error || 'Location not found', 'danger');
        }
    } catch (error) {
        showAlert('Error searching location: ' + error.message, 'danger');
    }
}

// Update GeoJSON from drawn items
function updateGeoJSON() {
    if (drawnItems.getLayers().length === 0) {
        currentGeoJSON = null;
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('viewGeoJSONBtn').disabled = true;
        return;
    }

    const geoJson = drawnItems.toGeoJSON();
    currentGeoJSON = {
        type: 'FeatureCollection',
        features: geoJson.features || [geoJson]
    };


    document.getElementById('downloadBtn').disabled = false;
    document.getElementById('viewGeoJSONBtn').disabled = false;
}

// Update GeoJSON display


// Download AOI
async function downloadAOI() {
    if (!currentGeoJSON) {
        showAlert('No AOI to download', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/download_aoi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ geojson: currentGeoJSON })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'aoi.geojson';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showAlert('AOI downloaded successfully!', 'success');
        } else {
            const data = await response.json();
            showAlert(data.error || 'Failed to download AOI', 'danger');
        }
    } catch (error) {
        showAlert('Error downloading file: ' + error.message, 'danger');
    }
}

// Clear map
function clearMap() {
    drawnItems.clearLayers();
    currentGeoJSON = null;
    document.getElementById('downloadBtn').disabled = true;
    document.getElementById('viewGeoJSONBtn').disabled = true;
}

// Show alert
function showAlert(message, type) {
    const alertBox = document.getElementById('alertBox');
    const alertText = document.getElementById('alertText');
    if (!alertBox || !alertText) return;

    alertBox.className = `alert alert-${type}`;
    alertText.textContent = message;
    alertBox.style.display = 'block';

    // Scroll to alert
    alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 5000);
}

// Update map from coordinates input
function updateMapFromCoordinates() {
    const latInput = document.getElementById('latitude');
    const lonInput = document.getElementById('longitude');

    const lat = parseFloat(latInput.value);
    const lon = parseFloat(lonInput.value);

    if (isNaN(lat) || isNaN(lon)) {
        return; // Invalid input, do nothing
    }

    if (lat < -90 || lat > 90) {
        showAlert('Latitude must be between -90 and 90', 'warning');
        return;
    }

    if (lon < -180 || lon > 180) {
        showAlert('Longitude must be between -180 and 180', 'warning');
        return;
    }

    map.setView([lat, lon], map.getZoom());

    // Update or add marker
    // Note: We might want to keep track of a specific search marker if we want to move it
    // For now, let's just add a new one or move the existing one if we can track it.
    // Since searchLocation adds a marker but doesn't save it to a variable accessible here easily without refactoring,
    // let's just add a new marker for now, or clear previous markers if we want to be cleaner.
    // But to be simple and consistent with searchLocation, let's just add it.
    // Actually, let's try to be a bit cleaner.

    L.marker([lat, lon]).addTo(map)
        .bindPopup(`📍 Custom Location <br>${lat.toFixed(6)}, ${lon.toFixed(6)}`)
        .openPopup();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initMap();

    // Allow Enter key to search
    document.getElementById('locationSearch').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            searchLocation();
        }
    });

    // Add event listeners for latitude and longitude inputs
    const latInput = document.getElementById('latitude');
    const lonInput = document.getElementById('longitude');

    if (latInput && lonInput) {
        ['change', 'input'].forEach(evt => {
            latInput.addEventListener(evt, updateMapFromCoordinates);
            lonInput.addEventListener(evt, updateMapFromCoordinates);
        });
    }
});

// View GeoJSON in modal
function viewGeoJSON() {
    if (!currentGeoJSON) {
        showAlert('No AOI to view', 'warning');
        return;
    }

    const content = JSON.stringify(currentGeoJSON, null, 2);
    document.getElementById('modalGeoJSONContent').textContent = content;

    const modal = new bootstrap.Modal(document.getElementById('geojsonModal'));
    modal.show();
}

// Copy GeoJSON to clipboard
function copyGeoJSON() {
    if (!currentGeoJSON) {
        return;
    }

    const content = JSON.stringify(currentGeoJSON, null, 2);
    navigator.clipboard.writeText(content).then(() => {
        showAlert('GeoJSON copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showAlert('Failed to copy to clipboard', 'danger');
    });
}


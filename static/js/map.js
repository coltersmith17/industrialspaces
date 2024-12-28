document.addEventListener('DOMContentLoaded', function() {
    // Initialize map if container exists
    const mapContainer = document.getElementById('propertyMap');
    if (mapContainer) {
        initMap();
    }
});

function initMap() {
    // Get property coordinates from data attributes
    const lat = parseFloat(document.getElementById('propertyMap').dataset.lat);
    const lng = parseFloat(document.getElementById('propertyMap').dataset.lng);

    // Create map
    const map = L.map('propertyMap').setView([lat, lng], 13);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add marker for property location
    L.marker([lat, lng]).addTo(map)
        .bindPopup(document.getElementById('propertyMap').dataset.title)
        .openPopup();
}

// Function to initialize map for multiple properties
function initPropertiesMap(properties) {
    // Center on Salt Lake City
    const map = L.map('propertyMap').setView([40.7608, -111.8910], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add markers for all properties
    properties.forEach(property => {
        L.marker([property.lat, property.lng])
            .addTo(map)
            .bindPopup(`
                <strong>${property.title}</strong><br>
                ${property.location}<br>
                <a href="/property/${property.id}">View Details</a>
            `);
    });
}
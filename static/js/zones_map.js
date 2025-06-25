window.addEventListener('DOMContentLoaded', () => {
  const map = L.map('zones-map').setView([42.8746, 74.6122], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const group = L.featureGroup().addTo(map);

  if (window.deliveryZones && window.deliveryZones.length) {
    window.deliveryZones.forEach(zone => {
      if (zone.geometry) {
        const layer = L.geoJSON({ type: 'Feature', geometry: zone.geometry }, {
          style: { color: zone.color }
        });
        layer.bindPopup(zone.name);
        group.addLayer(layer);
      }
    });
  }

  if (window.workArea && window.workArea.geometry) {
    const waLayer = L.geoJSON(window.workArea, {
      style: { color: '#888888', opacity: 0.2, fillOpacity: 0.1 }
    });
    group.addLayer(waLayer);
  }

  if (group.getLayers().length) {
    map.fitBounds(group.getBounds());
  }
});

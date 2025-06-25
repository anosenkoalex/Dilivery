window.addEventListener('DOMContentLoaded', () => {
  const map = L.map('zones-map').setView([42.8746, 74.6122], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  Promise.all([
    fetch('/api/zones').then(r => r.json()),
    fetch('/api/work-area').then(r => r.json())
  ]).then(([zones, workArea]) => {
    const group = L.featureGroup().addTo(map);
    if (zones && zones.features) {
      zones.features.forEach(f => {
        const layer = L.geoJSON(f, {
          style: { color: f.properties.color }
        });
        layer.bindPopup(f.properties.name);
        group.addLayer(layer);
      });
    }
    if (workArea && workArea.geometry) {
      const waLayer = L.geoJSON(workArea, {
        style: { color: '#777777', weight: 1, fillOpacity: 0.2, dashArray: '5 5' }
      });
      group.addLayer(waLayer);
    }
    if (group.getLayers().length) {
      map.fitBounds(group.getBounds());
    }
  });
});

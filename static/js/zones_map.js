window.addEventListener('DOMContentLoaded', () => {
  const map = L.map('zones-map').setView([42.8746, 74.6122], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const group = L.featureGroup().addTo(map);

  Promise.all([
    fetch('/api/zones').then(r => r.json()),
    fetch('/api/work-area').then(r => r.json())
  ]).then(([zones, workArea]) => {
    if (zones && zones.features) {
      zones.features.forEach(feature => {
        const layer = L.geoJSON(feature, {
          style: { color: feature.properties.color }
        });
        if (feature.properties.name) {
          layer.bindTooltip(feature.properties.name, { permanent: false });
        }
        group.addLayer(layer);
      });
    }

    if (workArea && workArea.geometry) {
      const waLayer = L.geoJSON(workArea, {
        style: {
          color: '#555',
          fillOpacity: 0.05,
          dashArray: '4',
          weight: 1
        }
      });
      group.addLayer(waLayer);
    }

    if (group.getLayers().length) {
      map.fitBounds(group.getBounds());
    }
  });
});

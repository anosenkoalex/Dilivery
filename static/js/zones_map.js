window.addEventListener('DOMContentLoaded', () => {
  const map = L.map('zones-map').setView([42.8746, 74.6122], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const group = L.featureGroup().addTo(map);

  async function loadMapData() {
    group.clearLayers();

    const [workArea, zones] = await Promise.all([
      fetch('/api/work-area').then(r => r.json()),
      fetch('/api/zones').then(r => r.json())
    ]);

    if (workArea && workArea.geometry) {
      L.geoJSON(workArea, {
        style: {
          color: '#555',
          weight: 2,
          dashArray: '4',
          fillOpacity: 0.07
        }
      }).addTo(group);
    }

    const features = zones && (zones.features || zones);
    if (features && Array.isArray(features)) {
      features.forEach(f => {
        const layer = L.geoJSON(f, {
          style: {
            color: f.properties ? f.properties.color : f.color,
            weight: 2,
            fillOpacity: 0.2
          }
        });
        const name = f.properties ? f.properties.name : f.name;
        if (name) {
          layer.bindTooltip(name);
        }
        group.addLayer(layer);
      });
    }

    if (group.getLayers().length) {
      map.fitBounds(group.getBounds());
    }
  }

  loadMapData();

  // Expose for reloading after create/edit/delete actions
  window.refreshZonesMap = loadMapData;
});

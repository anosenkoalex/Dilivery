window.addEventListener('DOMContentLoaded', () => {
  const colorInput = document.getElementById('colorInput');
  const geoInput = document.getElementById('geojsonInput');
  const form = document.querySelector('form');
  const map = L.map('zoneMap').setView([42.8746, 74.6122], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);

  let workAreaGeoJSON = null;

  fetch('/api/work-area')
    .then(r => r.json())
    .then(data => {
      if (data && data.geometry) {
        workAreaGeoJSON = data;
        const waLayer = L.geoJSON(data, {
          style: { color: '#777777', weight: 1, fillOpacity: 0.2, dashArray: '5 5' }
        }).addTo(map);
        map.fitBounds(waLayer.getBounds());
      }
      loadExisting();
    });

  function loadExisting() {
    if (window.existingZone && window.existingZone.geometry && window.existingZone.geometry.coordinates) {
      const poly = L.geoJSON(window.existingZone, { style: { color: colorInput.value } });
      drawnItems.addLayer(poly);
      map.fitBounds(poly.getBounds());
    }
  }

  const drawControl = new L.Control.Draw({
    edit: { featureGroup: drawnItems, remove: true },
    draw: { polygon: true, marker:false, polyline:false, rectangle:false, circle:false, circlemarker:false }
  });
  map.addControl(drawControl);

  function updateGeo() {
    let gj = null;
    drawnItems.eachLayer(l => {
      if (l.toGeoJSON) {
        if (l.setStyle) l.setStyle({ color: colorInput.value });
        gj = l.toGeoJSON();
      }
    });
    geoInput.value = gj ? JSON.stringify(gj) : '';
  }

  map.on('draw:created', e => {
    const layer = e.layer;
    const zone = layer.toGeoJSON();
    if (workAreaGeoJSON && !turf.booleanWithin(zone, workAreaGeoJSON)) {
      alert('Зона должна быть внутри рабочей области');
      return;
    }
    drawnItems.clearLayers();
    drawnItems.addLayer(layer);
    updateGeo();
  });

  map.on('draw:edited', updateGeo);
  map.on('draw:deleted', updateGeo);

  colorInput.addEventListener('change', updateGeo);

  form.addEventListener('submit', e => {
    const layers = drawnItems.getLayers();
    if (layers.length === 0) {
      alert('Нарисуйте зону на карте');
      e.preventDefault();
      return;
    }
    const zoneGeoJSON = layers[0].toGeoJSON();
    geoInput.value = JSON.stringify(zoneGeoJSON);
  });
});

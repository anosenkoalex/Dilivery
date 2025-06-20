function initMap(orders, zones) {
  const map = L.map('map').setView([42.8746, 74.6122], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  zones.forEach(function(z) {
    var polygon = L.polygon(z.polygon.map(function(p){ return [p[1], p[0]]; }), {color: z.color}).addTo(map);
    polygon.bindPopup(z.name);
  });

  orders.forEach(function(o){
    if(o.lat && o.lng){
      var marker = L.marker([o.lat, o.lng]).addTo(map);
      var popup = '<b>Заказ #' + o.id + '</b><br>' + o.address + '<br>Статус: ' + o.status;
      marker.bindPopup(popup);
    }
  });
}

function initZonesMap(zones) {
  const map = L.map('zones-map').setView([42.8746, 74.6122], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  var group = L.featureGroup().addTo(map);
  zones.forEach(function(z) {
    if (z.polygon && z.polygon.length) {
      var poly = L.polygon(z.polygon.map(function(p){ return [p[1], p[0]]; }), {color: z.color});
      poly.bindPopup(z.name);
      group.addLayer(poly);
    }
  });

  if (group.getLayers().length) {
    map.fitBounds(group.getBounds());
  }
}
document.addEventListener('DOMContentLoaded', function(){
  var modalEl = document.getElementById('setPointModal');
  if(!modalEl) return;
  var map, marker, currentOrder, latInputId, lonInputId;
  modalEl.addEventListener('shown.bs.modal', function(e){
    var trg = e.relatedTarget;
    currentOrder = trg.getAttribute('data-id');
    latInputId = trg.getAttribute('data-input-lat');
    lonInputId = trg.getAttribute('data-input-lon');
    var mapDiv = document.getElementById('pointMap');
    if (map) {
      map.off();
      map.remove();
    }
    mapDiv.innerHTML = '';
    var startLat = 42.8746, startLon = 74.6122, zoom = 13;
    if(latInputId && lonInputId){
      var latEl = document.getElementById(latInputId);
      var lonEl = document.getElementById(lonInputId);
      if(latEl && latEl.value && lonEl && lonEl.value){
        startLat = parseFloat(latEl.value);
        startLon = parseFloat(lonEl.value);
        zoom = 16;
      }
    }
    map = L.map('pointMap').setView([startLat,startLon], zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom:19,
      attribution:'&copy; OpenStreetMap contributors'
    }).addTo(map);
    var group = L.featureGroup().addTo(map);
    if(window.zonesData){
      window.zonesData.forEach(function(z){
        if(z.polygon && z.polygon.length){
          var poly = L.polygon(z.polygon.map(function(p){return [p[1], p[0]];}), {color:z.color});
          poly.bindPopup(z.name);
          group.addLayer(poly);
        }
      });
      if(group.getLayers().length){
        map.fitBounds(group.getBounds());
      }
    }
    marker = null;
    if(zoom === 16){
      marker = L.marker([startLat,startLon], {draggable: true}).addTo(map);
      marker.on('dragend', function(ev){ marker = ev.target; });
    }
    map.on('click', function(ev){
      if(marker) map.removeLayer(marker);
      marker = L.marker(ev.latlng, {draggable: true}).addTo(map);
      marker.on('dragend', function(ev){ marker = ev.target; });
    });
    var searchInput = document.getElementById('addressSearch');
    if(searchInput){
      searchInput.value = '';
      searchInput.onkeydown = function(ev){
        if(ev.key === 'Enter'){
          ev.preventDefault();
          const query = ev.target.value;
          fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`)
            .then(res=>res.json())
            .then(data=>{
              if(data && data.length){
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);
                map.setView([lat,lon],16);
                if(marker) map.removeLayer(marker);
                marker = L.marker([lat,lon], {draggable: true}).addTo(map);
                marker.on('dragend', function(ev){ marker = ev.target; });
              }
            });
        }
      };
    }
    setTimeout(function(){ map.invalidateSize(); }, 0);
  });
  document.getElementById('savePointBtn').addEventListener('click', function(){
    if(!marker) return;
    var latlng = marker.getLatLng();
    if(latInputId && lonInputId){
      document.getElementById(latInputId).value = latlng.lat;
      document.getElementById(lonInputId).value = latlng.lng;
      bootstrap.Modal.getInstance(modalEl).hide();
    }else{
      fetch('/orders/set_point', {
        method:'POST',
        headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:new URLSearchParams({order_id: currentOrder, lat: latlng.lat, lon: latlng.lng})
      }).then(r=>r.json()).then(function(data){
        if(data.success){
          var row = document.querySelector('tr[data-id="'+currentOrder+'"]');
          if(row){
            row.classList.remove('table-warning');
            row.querySelector('.zone-cell').textContent = data.zone || 'Не определена';
            row.querySelector('.coords-cell').textContent = '✔';
            var ccell = row.querySelector('.courier-cell');
            if(ccell) ccell.textContent = data.courier || '—';
          }
          bootstrap.Modal.getInstance(modalEl).hide();
        }
      });
    }
  });
});

let currentJobId = null;

function startImportMonitor(jobId, title) {
  currentJobId = jobId;
  const titleEl = document.getElementById('import-title');
  if (titleEl) {
    titleEl.textContent = `Импорт: ${title}`;
  }
  pollImportStatus();
}

function pollImportStatus() {
  if (!currentJobId) return;

  fetch(`/import/status/${currentJobId}`)
    .then(res => res.json())
    .then(data => {
      const pct = data.total_rows ? (data.processed / data.total_rows * 100) : 0;
      const bar = document.getElementById('import-bar');
      if (bar) {
        bar.style.width = pct + '%';
      }
      const countEl = document.getElementById('import-count');
      if (countEl) {
        countEl.textContent = `${data.processed}/${data.total_rows}`;
      }

      if (data.status === 'done' || data.status === 'error') {
        const list = document.getElementById('import-errors');
        if (list) {
          list.innerHTML = '';
          if (data.errors) {
            data.errors.forEach(e => {
              const li = document.createElement('li');
              li.textContent = e;
              list.appendChild(li);
            });
          }
        }
        currentJobId = null;
      } else {
        setTimeout(pollImportStatus, 1500);
      }
    });
}

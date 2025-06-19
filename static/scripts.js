function initMap(orders, zones) {
  var map = L.map('map').setView([42.8746, 74.6122], 13);
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
document.addEventListener('DOMContentLoaded', function(){
  var modalEl = document.getElementById('setPointModal');
  if(!modalEl) return;
  var map, marker, currentOrder;
  modalEl.addEventListener('shown.bs.modal', function(e){
    currentOrder = e.relatedTarget.getAttribute('data-id');
    var mapDiv = document.getElementById('pointMap');
    mapDiv.innerHTML = '';
    map = L.map('pointMap').setView([42.8746,74.6122],13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom:19,
      attribution:'&copy; OpenStreetMap contributors'
    }).addTo(map);
    marker = null;
    map.on('click', function(ev){
      if(marker) map.removeLayer(marker);
      marker = L.marker(ev.latlng).addTo(map);
    });
  });
  document.getElementById('savePointBtn').addEventListener('click', function(){
    if(!marker) return;
    var latlng = marker.getLatLng();
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
        }
        bootstrap.Modal.getInstance(modalEl).hide();
      }
    });
  });
});

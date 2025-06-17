function initMap(orders, zones) {
  var map = L.map('map').setView([55.75, 37.65], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  zones.forEach(function(z) {
    var polygon = L.polygon(z.polygon_json.map(function(p){return [p[1],p[0]];}), {color: z.color}).addTo(map);
    polygon.bindPopup(z.name);
  });

  orders.forEach(function(o){
    if(o.latitude && o.longitude){
      var marker = L.marker([o.latitude, o.longitude]).addTo(map);
      marker.bindPopup('<b>'+o.order_number+'</b><br>'+o.client_name+'<br>'+o.address+'<br>Статус: '+o.status);
    }
  });
}

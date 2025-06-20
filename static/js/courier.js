window.addEventListener('DOMContentLoaded', function(){
  const takeBtn = document.getElementById('takeBtn');
  const ordersBody = document.getElementById('ordersBody');
  const counterEl = document.getElementById('counterText');

  function updateCounter(){
    const count = document.querySelectorAll('.order-check').length;
    if(counterEl) counterEl.textContent = count;
  }

  function updateMarker(id, status){
    const m = window.courierMarkers[id];
    if(!m) return;
    if(status === 'out_for_delivery'){
      m.setStyle({color:'orange', fillColor:'orange'});
    }else if(status === 'delivered'){
      m.remove();
      delete window.courierMarkers[id];
      return;
    }
    const popup = `<b>Заказ #${id}</b><br>${m.options.address}<br>${status}`;
    m.bindPopup(popup);
  }

  takeBtn && takeBtn.addEventListener('click', function(){
    const ids = Array.from(document.querySelectorAll('.order-check:checked')).map(cb => cb.closest('tr').dataset.id);
    if(!ids.length) return;
    fetch('/courier/take', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ids: ids})
    }).then(r=>r.json()).then(data=>{
      if(data.success){
        ids.forEach(function(id){
          const row = document.querySelector(`tr[data-id="${id}"]`);
          if(row){
            row.querySelector('.order-check').remove();
            row.querySelector('.status-cell').textContent = 'out_for_delivery';
            const actions = row.querySelector('.actions');
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-success deliver-btn';
            btn.textContent = 'Доставлен';
            btn.addEventListener('click', deliverHandler);
            actions.appendChild(btn);
          }
          updateMarker(id, 'out_for_delivery');
        });
        updateCounter();
      }
    });
  });

  function deliverHandler(ev){
    const row = ev.target.closest('tr');
    const id = row.dataset.id;
    fetch(`/courier/delivered/${id}`, {method:'POST'}).then(r=>r.json()).then(data=>{
      if(data.success){
        row.remove();
        updateMarker(id, 'delivered');
        updateCounter();
      }
    });
  }

  document.querySelectorAll('.deliver-btn').forEach(btn => btn.addEventListener('click', deliverHandler));

  // map init
  const mapEl = document.getElementById('courierMap');
  if(mapEl){
    const map = L.map('courierMap').setView([42.8746,74.6122], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19}).addTo(map);
    window.courierMarkers = {};
    courierOrders.forEach(function(o){
      if(o.lat && o.lng){
        const color = o.status === 'prepared' ? 'blue' : (o.status === 'out_for_delivery' ? 'orange' : 'green');
        const m = L.circleMarker([o.lat, o.lng], {radius:8, color:color, fillColor:color, fillOpacity:1}).addTo(map);
        m.options.address = o.address;
        m.bindPopup(`<b>Заказ #${o.order_number}</b><br>${o.address}<br>${o.status}`);
        window.courierMarkers[o.id] = m;
      }
    });
  }

  updateCounter();
});

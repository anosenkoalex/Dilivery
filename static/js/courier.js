window.addEventListener('DOMContentLoaded', function(){
  const ordersBody = document.getElementById('ordersBody');
  const counterEl = document.getElementById('counterText');
  const acceptAllBtn = document.getElementById('acceptAllBtn');
  const noOrdersMsg = document.getElementById('noOrdersMsg');
  let map;

  function updateCounter(){
    const count = document.querySelectorAll('tr[data-status="Подготовлен к доставке"]').length;
    if(counterEl) counterEl.textContent = count;
    if(acceptAllBtn) acceptAllBtn.style.display = count > 0 ? '' : 'none';
    if(noOrdersMsg) noOrdersMsg.style.display = count > 0 ? 'none' : '';
  }

  function updateMarker(id, status){
    const m = window.courierMarkers[id];
    if(!m) return;
    if(status === 'Выдано на доставку'){
      m.setStyle({color:'orange', fillColor:'orange'});
    }else if(status === 'Доставлен'){
      m.remove();
      delete window.courierMarkers[id];
      return;
    }else if(status === 'Проблема'){
      m.setStyle({color:'red', fillColor:'red'});
    }
    const popup = `<b>Заказ #${id}</b><br>${m.options.address}<br>${status}`;
    m.bindPopup(popup);
  }


  function takeHandler(ev){
    const row = ev.target.closest('tr');
    const id = row.dataset.id;
    fetch('/courier/take', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ids:[id]})
    }).then(r=>r.json()).then(data=>{
      if(data.success){
        row.dataset.status = 'Выдано на доставку';
        ev.target.remove();
        row.querySelector('.status-cell').textContent = 'Выдано на доставку';
        const actions = row.querySelector('.actions');
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-success deliver-btn';
        btn.textContent = 'Доставлен';
        btn.addEventListener('click', deliverHandler);
        actions.appendChild(btn);
        updateMarker(id, 'Выдано на доставку');
        updateCounter();
      }
    });
  }

  function deliverHandler(ev){
    const row = ev.target.closest('tr');
    const id = row.dataset.id;
    fetch(`/courier/delivered/${id}`, {method:'POST'}).then(r=>r.json()).then(data=>{
      if(data.success){
        row.remove();
        updateMarker(id, 'Доставлен');
        updateCounter();
      }
    });
  }

  function problemHandler(ev){
    const row = ev.target.closest('tr');
    const id = row.dataset.id;
    const comment = prompt('Кратко опишите проблему');
    fetch(`/courier/problem/${id}`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({comment: comment || ''})
    }).then(r=>r.json()).then(data=>{
      if(data.success){
        row.dataset.status = 'Проблема';
        row.querySelector('.status-cell').textContent = 'Проблема';
        row.querySelector('.deliver-btn').remove();
        ev.target.remove();
        updateMarker(id, 'Проблема');
        updateCounter();
      }
    });
  }

  document.querySelectorAll('.deliver-btn').forEach(btn => btn.addEventListener('click', deliverHandler));
  document.querySelectorAll('.problem-btn').forEach(btn => btn.addEventListener('click', problemHandler));
  document.querySelectorAll('.take-btn').forEach(btn => btn.addEventListener('click', takeHandler));

  if(acceptAllBtn){
    acceptAllBtn.addEventListener('click', function(){
      fetch('/courier/accept_all', {method:'POST'})
        .then(r=>r.json())
        .then(data=>{ if(data.success){ window.location.reload(); } });
    });
  }

  // map init
  const mapEl = document.getElementById('courierMap');
  function initMap(){
    if(map || !mapEl) return;
    map = L.map('courierMap').setView([42.8746,74.6122], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19}).addTo(map);
    window.courierMarkers = {};
    courierOrders.forEach(function(o){
      if(o.lat && o.lng){
        let color = 'green';
        if(o.status === 'Подготовлен к доставке') color = 'blue';
        else if(o.status === 'Выдано на доставку') color = 'orange';
        else if(o.status === 'Проблема') color = 'red';
        const m = L.circleMarker([o.lat, o.lng], {radius:8, color:color, fillColor:color, fillOpacity:1}).addTo(map);
        m.options.address = o.address;
        m.bindPopup(`<b>Заказ #${o.order_number}</b><br>${o.address}<br>${o.status}`);
        window.courierMarkers[o.id] = m;
      }
    });
    setTimeout(() => map.invalidateSize(), 0);
  }

  const mapTab = document.getElementById('map-tab');
  if(mapTab){
    mapTab.addEventListener('shown.bs.tab', initMap);
    if(mapTab.classList.contains('active')){
      initMap();
    }
  }

  updateCounter();
});

function closeMapModal() {
    const modal = document.getElementById('mapModal');
    if (modal) {
        modal.style.display = 'none';
    }
    if (window.orderMap) {
        window.orderMap.off();
        window.orderMap.remove();
        window.orderMap = null;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('orderSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const value = this.value.toLowerCase();
            document.querySelectorAll('.orders-table tbody tr').forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(value) ? '' : 'none';
            });
        });
    }
    document.body.addEventListener('click', function (e) {
        const btn = e.target.closest('.set-coords');
        if (btn) {
            const id = btn.dataset.orderId;
            if (id) openMapModal(id);
        }
    });
});

function openMapModal(orderId) {
    const modal = document.getElementById('mapModal');
    if (!modal) return;
    modal.style.display = 'block';
    const container = document.getElementById('mapContainer');
    if (window.orderMap) {
        window.orderMap.off();
        window.orderMap.remove();
        window.orderMap = null;
    }
    container.innerHTML = '';
    window.orderMap = L.map('mapContainer').setView([42.87, 74.6], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(window.orderMap);
    const group = L.featureGroup().addTo(window.orderMap);
    if (window.zonesData) {
        window.zonesData.forEach(z => {
            if (z.polygon && z.polygon.length) {
                const poly = L.polygon(z.polygon.map(p => [p[1], p[0]]), {color: z.color, interactive:false});
                poly.bindPopup(z.name);
                group.addLayer(poly);
            }
        });
        if (group.getLayers().length) {
            window.orderMap.fitBounds(group.getBounds());
        }
    }
    let marker;
    window.orderMap.on('click', function(e) {
        if (marker) window.orderMap.removeLayer(marker);
        marker = L.marker(e.latlng, {draggable: true}).addTo(window.orderMap);
        const pos = e.latlng;
        modal.dataset.lat = pos.lat;
        modal.dataset.lng = pos.lng;
        marker.on('dragend', function(ev){
            const p = ev.target.getLatLng();
            modal.dataset.lat = p.lat;
            modal.dataset.lng = p.lng;
        });
    });
    const searchInput = document.getElementById('addressSearchModal');
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
                            window.orderMap.setView([lat,lon],16);
                            if(marker) window.orderMap.removeLayer(marker);
                            marker = L.marker([lat,lon], {draggable:true}).addTo(window.orderMap);
                            modal.dataset.lat = lat;
                            modal.dataset.lng = lon;
                            marker.on('dragend', function(ev){
                                const p = ev.target.getLatLng();
                                modal.dataset.lat = p.lat;
                                modal.dataset.lng = p.lng;
                            });
                        }
                    });
            }
        };
    }
    setTimeout(() => { window.orderMap.invalidateSize(); }, 0);

    document.getElementById('saveCoordsBtn').onclick = () => {
        if (!modal.dataset.lat || !modal.dataset.lng) return;
        fetch(`/orders/set_coordinates/${orderId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latitude: modal.dataset.lat,
                longitude: modal.dataset.lng
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data && data.success) {
                const row = document.querySelector(`tr[data-id="${orderId}"]`);
                if (row) {
                    row.classList.remove('table-warning');
                    const ccell = row.querySelector('.coords-cell');
                    if (ccell) ccell.textContent = '✔';
                    const zcell = row.querySelector('.zone-cell');
                    if (zcell && 'zone' in data) zcell.textContent = data.zone || 'Не определена';
                    const courierCell = row.querySelector('.courier-cell');
                    if (courierCell && 'courier' in data) courierCell.textContent = data.courier || '—';
                }
            }
            closeMapModal();
        });
    };
}

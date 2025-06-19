function closeMapModal() {
    const modal = document.getElementById('mapModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function openMapModal(orderId) {
    const modal = document.getElementById('mapModal');
    if (!modal) return;
    modal.style.display = 'block';
    const container = document.getElementById('mapContainer');
    container.innerHTML = '';
    const map = L.map('mapContainer').setView([42.87, 74.6], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let marker;
    map.on('click', function(e) {
        if (marker) map.removeLayer(marker);
        marker = L.marker(e.latlng).addTo(map);
        modal.dataset.lat = e.latlng.lat;
        modal.dataset.lng = e.latlng.lng;
    });
    setTimeout(() => { map.invalidateSize(); }, 0);

    document.getElementById('saveCoordsBtn').onclick = () => {
        if (!modal.dataset.lat || !modal.dataset.lng) return;
        fetch(`/api/orders/${orderId}/coordinates`, {
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
                }
            }
            closeMapModal();
        });
    };
}

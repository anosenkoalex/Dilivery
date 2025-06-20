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
    let marker;
    window.orderMap.on('click', function(e) {
        if (marker) window.orderMap.removeLayer(marker);
        marker = L.marker(e.latlng).addTo(window.orderMap);
        modal.dataset.lat = e.latlng.lat;
        modal.dataset.lng = e.latlng.lng;
    });
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
                }
            }
            closeMapModal();
        });
    };
}

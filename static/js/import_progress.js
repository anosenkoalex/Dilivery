document.addEventListener('DOMContentLoaded', function () {
  const toastEl = document.getElementById('import-toast');
  if (!toastEl) return;
  const toast = new bootstrap.Toast(toastEl, { autohide: false });
  const bar = document.getElementById('import-progress-bar');
  const txt = document.getElementById('import-progress-text');
  const closeBtn = toastEl.querySelector('.btn-close');
  const socket = io();

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      sessionStorage.setItem('import_hidden', 'true');
    });
  }

  function update(data) {
    if (!data) {
      toast.hide();
      return;
    }
    const pct = data.total ? (data.processed / data.total) * 100 : 0;
    bar.style.width = pct + '%';
    txt.textContent = `${data.processed}/${data.total}`;
    if (data.status === 'running') {
      if (!sessionStorage.getItem('import_hidden')) {
        toast.show();
      }
    } else {
      setTimeout(() => toast.hide(), 2000);
    }
  }

  socket.on('import_progress', update);

  fetch('/api/import/active')
    .then((r) => (r.status === 200 ? r.json() : null))
    .then(update);
});

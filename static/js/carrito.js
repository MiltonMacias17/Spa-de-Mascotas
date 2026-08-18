function getCookie(name) {
  const val = document.cookie.split('; ').find(r => r.startsWith(name + '='));
  return val ? decodeURIComponent(val.split('=')[1]) : null;
}

document.addEventListener('DOMContentLoaded', function () {
  // Botones "Agregar al carrito" en el catálogo
  document.querySelectorAll('.btn-agregar').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const productoId = this.dataset.producto;
      const nombre     = this.dataset.nombre;
      fetch('/tienda/carrito/agregar/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: 'producto_id=' + productoId + '&cantidad=1',
      })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          mostrarToast('✅ ' + nombre + ' agregado al carrito');
          const contador = document.querySelector('.btn-outline[href*="carrito"]');
          if (contador) contador.textContent = '🛒 Carrito (' + data.total_items + ')';
        }
      });
    });
  });

  // Botón agregar en página de detalle
  const btnDetalle = document.querySelector('.btn-agregar-detalle');
  if (btnDetalle) {
    btnDetalle.addEventListener('click', function () {
      const productoId = this.dataset.producto;
      const cantidad   = document.getElementById('cantidad')?.value || 1;
      const varianteId = document.getElementById('select-variante')?.value || '';
      let body = 'producto_id=' + productoId + '&cantidad=' + cantidad;
      if (varianteId) body += '&variante_id=' + varianteId;
      fetch('/tienda/carrito/agregar/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: body,
      })
      .then(r => r.json())
      .then(data => {
        if (data.ok) mostrarToast('✅ Agregado al carrito');
      });
    });
  }
});

function mostrarToast(msg) {
  const toast = document.createElement('div');
  toast.textContent = msg;
  toast.style.cssText = `
    position:fixed; bottom:1.5rem; right:1.5rem;
    background:#2C3E50; color:#fff; padding:.75rem 1.25rem;
    border-radius:8px; font-size:.875rem; z-index:9999;
    box-shadow:0 4px 16px rgba(0,0,0,.2); animation: fadeIn .2s;
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

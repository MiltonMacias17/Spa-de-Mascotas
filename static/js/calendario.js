// Calendario simple con CSS Grid — sin dependencias externas
document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('calendar');
  if (!container) return;

  const now = new Date();
  let year  = now.getFullYear();
  let month = now.getMonth();

  function render() {
    const firstDay  = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const monthNames = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                        'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

    // Crear mapa de eventos por fecha
    const eventosPorDia = {};
    if (typeof eventosCalendario !== 'undefined') {
      eventosCalendario.forEach(ev => {
        const d = ev.start.substring(0, 10);
        if (!eventosPorDia[d]) eventosPorDia[d] = [];
        eventosPorDia[d].push(ev);
      });
    }

    let html = `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:1rem 1.25rem;border-bottom:1px solid #dee2e6">
        <button onclick="calNav(-1)" style="background:none;border:1px solid #dee2e6;border-radius:6px;padding:.3rem .7rem;cursor:pointer">‹</button>
        <strong>${monthNames[month]} ${year}</strong>
        <button onclick="calNav(1)"  style="background:none;border:1px solid #dee2e6;border-radius:6px;padding:.3rem .7rem;cursor:pointer">›</button>
      </div>
      <div style="display:grid;grid-template-columns:repeat(7,1fr);text-align:center">
    `;
    ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'].forEach(d => {
      html += `<div style="padding:.5rem;font-size:.75rem;font-weight:600;color:#6c757d;text-transform:uppercase">${d}</div>`;
    });

    // Días vacíos iniciales
    for (let i = 0; i < firstDay; i++) {
      html += '<div style="padding:.5rem;min-height:80px"></div>';
    }

    const todayStr = now.toISOString().substring(0, 10);
    for (let d = 1; d <= daysInMonth; d++) {
      const pad = String(d).padStart(2, '0');
      const mon = String(month + 1).padStart(2, '0');
      const dateStr = `${year}-${mon}-${pad}`;
      const isToday = dateStr === todayStr;
      const eventos = eventosPorDia[dateStr] || [];

      html += `<div style="padding:.35rem;min-height:80px;border:1px solid #f1f3f5;${isToday ? 'background:#e3f0fb' : ''}">
        <div style="font-weight:${isToday ? 700 : 400};color:${isToday ? '#4A90D9' : 'inherit'};margin-bottom:.25rem">${d}</div>`;
      eventos.slice(0, 3).forEach(ev => {
        html += `<a href="${ev.url || '#'}" style="display:block;background:${ev.color || '#4A90D9'};color:#fff;border-radius:4px;padding:.1rem .3rem;font-size:.7rem;margin-bottom:.1rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${ev.title}</a>`;
      });
      if (eventos.length > 3) html += `<span style="font-size:.7rem;color:#6c757d">+${eventos.length - 3} más</span>`;
      html += '</div>';
    }
    html += '</div>';
    container.innerHTML = html;
  }

  window.calNav = function (dir) {
    month += dir;
    if (month < 0) { month = 11; year--; }
    if (month > 11) { month = 0; year++; }
    render();
  };

  render();
});

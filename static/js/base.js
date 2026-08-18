function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}
// Auto-cerrar alertas después de 5 segundos
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => a.remove());
  }, 5000);
});

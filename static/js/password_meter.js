document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('id_password1');
  const bar   = document.getElementById('meter-bar');
  const label = document.getElementById('meter-label');
  if (!input) return;

  input.addEventListener('input', function () {
    const val = this.value;
    let score = 0;
    if (val.length >= 8)  score++;
    if (val.length >= 12) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[a-z]/.test(val)) score++;
    if (/\d/.test(val))    score++;
    if (/[!@#$%^&*()_+\-=\[\]{};:'",.?]/.test(val)) score++;

    const pct = Math.min(100, (score / 6) * 100);
    bar.style.width = pct + '%';

    if (score <= 2) {
      bar.style.background = '#dc3545';
      label.textContent = '⚠️ Contraseña débil';
      label.style.color = '#dc3545';
    } else if (score <= 4) {
      bar.style.background = '#ffc107';
      label.textContent = '⚡ Contraseña media';
      label.style.color = '#856404';
    } else {
      bar.style.background = '#28a745';
      label.textContent = '✅ Contraseña fuerte';
      label.style.color = '#155724';
    }
  });
});

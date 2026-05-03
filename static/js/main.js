// ── Role toggle ───────────────────────────────
function setRole(role) {
  document.getElementById('role-input').value = role;
  document.getElementById('opt-customer').classList.toggle('active', role === 'customer');
  document.getElementById('opt-worker').classList.toggle('active', role === 'worker');
  const wf = document.getElementById('worker-fields');
  if (wf) wf.style.display = role === 'worker' ? 'block' : 'none';
}

// ── Password check ────────────────────────────
function checkPass() {
  const p1  = document.getElementById('pw1');
  const p2  = document.getElementById('pw2');
  const err = document.getElementById('pw-err');
  if (p1 && p2 && p1.value !== p2.value) {
    if (err) err.style.display = 'block';
    return false;
  }
  if (err) err.style.display = 'none';
  return true;
}

// ── Auto-hide flashes ─────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    });
  }, 3500);

  // Apply saved theme on load
  applyTheme(
    localStorage.getItem('zariya_theme') || 'teal',
    localStorage.getItem('zariya_dark')  === 'true'
  );
});

// ── Toggle forms ──────────────────────────────
function toggleApply(jobId) {
  const f = document.getElementById('apply-form-' + jobId);
  if (f) f.style.display = f.style.display === 'none' ? 'block' : 'none';
}
function toggleReview(jobId) {
  const f = document.getElementById('review-' + jobId);
  if (f) f.style.display = f.style.display === 'none' ? 'block' : 'none';
}
function toggleCancel(jobId) {
  const f = document.getElementById('cancel-form-' + jobId);
  if (f) f.style.display = f.style.display === 'none' ? 'block' : 'none';
}
function toggleRequestForm(workerId) {
  document.querySelectorAll('.request-form-panel').forEach(p => {
    if (p.id !== 'req-form-' + workerId) p.style.display = 'none';
  });
  const f = document.getElementById('req-form-' + workerId);
  if (f) f.style.display = f.style.display === 'none' ? 'block' : 'none';
}

// ── Theme switcher ────────────────────────────
function applyTheme(color, dark) {
  document.documentElement.setAttribute('data-theme-color', color);
  document.documentElement.setAttribute('data-dark', dark ? 'true' : 'false');
  localStorage.setItem('zariya_theme', color);
  localStorage.setItem('zariya_dark',  dark);

  // Sync toggles if on settings page
  const darkToggle = document.getElementById('dark-toggle');
  if (darkToggle) darkToggle.classList.toggle('on', dark);
  document.querySelectorAll('.swatch').forEach(s => {
    s.classList.toggle('active', s.dataset.color === color);
  });
  const hiddenColor = document.getElementById('theme_color_input');
  const hiddenDark  = document.getElementById('dark_mode_input');
  if (hiddenColor) hiddenColor.value = color;
  if (hiddenDark)  hiddenDark.checked = dark;
}

function selectSwatch(color) {
  const dark = localStorage.getItem('zariya_dark') === 'true';
  applyTheme(color, dark);
}

function toggleDark() {
  const dark = localStorage.getItem('zariya_dark') !== 'true';
  const color = localStorage.getItem('zariya_theme') || 'teal';
  applyTheme(color, dark);
}

// ── Photo preview ──────────────────────────────
function previewPhoto(input, imgId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => {
      const img = document.getElementById(imgId);
      if (img) { img.src = e.target.result; img.style.display = 'block'; }
      const initials = img ? img.previousElementSibling : null;
      if (initials && initials.classList.contains('initials-text')) initials.style.display = 'none';
    };
    reader.readAsDataURL(input.files[0]);
  }
}

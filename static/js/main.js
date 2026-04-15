// Role toggle on signup page
function setRole(role) {
  document.getElementById('role-input').value = role;
  document.getElementById('opt-customer').classList.toggle('active', role === 'customer');
  document.getElementById('opt-worker').classList.toggle('active', role === 'worker');
  document.getElementById('worker-fields').style.display = role === 'worker' ? 'block' : 'none';
}

// Password match check
function checkPass() {
  const p1 = document.getElementById('pw1');
  const p2 = document.getElementById('pw2');
  const err = document.getElementById('pw-err');
  if (p1 && p2 && p1.value !== p2.value) {
    err.style.display = 'block';
    return false;
  }
  if (err) err.style.display = 'none';
  return true;
}

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    });
  }, 3500);
});

// Toggle apply form on browse jobs page
function toggleApply(jobId) {
  const form = document.getElementById('apply-form-' + jobId);
  if (form) {
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
  }
}

// Toggle review form on my jobs page
function toggleReview(jobId) {
  const form = document.getElementById('review-' + jobId);
  if (form) {
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
  }
}
/**
 * dark-mode.js — Runs immediately to prevent flash of wrong theme.
 */
(function () {
  var t = localStorage.getItem('eh-theme') || 'light';
  document.documentElement.setAttribute('data-theme', t);
})();

document.addEventListener('DOMContentLoaded', function () {
  var btn   = document.getElementById('themeBtn');
  var ico   = document.getElementById('themeIco');
  var lbl   = document.getElementById('themeLabel');
  if (!btn) return;

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('eh-theme', theme);
    if (theme === 'dark') {
      ico.className = 'bi bi-sun-fill';
      if (lbl) lbl.textContent = 'Light';
    } else {
      ico.className = 'bi bi-moon-stars-fill';
      if (lbl) lbl.textContent = 'Dark';
    }
  }

  // Apply current saved theme
  apply(document.documentElement.getAttribute('data-theme') || 'light');

  btn.addEventListener('click', function () {
    var cur  = document.documentElement.getAttribute('data-theme');
    apply(cur === 'dark' ? 'light' : 'dark');
  });
});

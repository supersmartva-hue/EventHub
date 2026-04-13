/**
 * EventHub — main.js
 * Handles: search autocomplete, notifications, flash auto-dismiss, theme
 */

// Helper: get CSRF token from meta tag
function getCSRF() {
  const m = document.querySelector('meta[name="csrf-token"]');
  return m ? m.content : '';
}

document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. Auto-dismiss flash messages ─────────────────────────── */
  document.querySelectorAll('.flash-msg').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s, transform .4s';
      el.style.opacity    = '0';
      el.style.transform  = 'translateX(30px)';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  /* ── 2. Navbar search autocomplete ──────────────────────────── */
  const input   = document.getElementById('navSearch');
  const box     = document.getElementById('suggestBox');

  if (input && box) {
    let timer;

    input.addEventListener('input', function () {
      clearTimeout(timer);
      const q = this.value.trim();
      if (q.length < 2) { box.classList.remove('open'); box.innerHTML = ''; return; }

      timer = setTimeout(() => {
        fetch(`/api/search/suggestions?q=${encodeURIComponent(q)}`)
          .then(r => r.json())
          .then(items => {
            if (!items.length) { box.classList.remove('open'); return; }
            box.innerHTML = items.map(it => `
              <div class="suggest-item" data-id="${it.id}">
                <span>${highlight(it.title, q)}</span>
                <span class="suggest-cat">${it.category}</span>
              </div>
            `).join('');
            box.classList.add('open');
            box.querySelectorAll('.suggest-item').forEach(el => {
              el.addEventListener('click', () => {
                window.location.href = `/events/${el.dataset.id}`;
              });
            });
          })
          .catch(() => {});
      }, 280);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        window.location.href = `/search?q=${encodeURIComponent(this.value)}`;
      }
    });

    document.addEventListener('click', function (e) {
      if (!input.contains(e.target)) box.classList.remove('open');
    });
  }

  /* ── 3. Notifications ────────────────────────────────────────── */
  const trigger  = document.getElementById('notifTrigger');
  const panel    = document.getElementById('notifPanel');
  const dot      = document.getElementById('notifDot');
  const scroll   = document.getElementById('notifScroll');
  const markBtn  = document.getElementById('markAllRead');

  if (trigger && panel) {

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      const wasOpen = panel.classList.contains('open');
      panel.classList.toggle('open');
      if (!wasOpen) fetchNotifs();
    });

    document.addEventListener('click', function (e) {
      if (!panel.contains(e.target) && e.target !== trigger) {
        panel.classList.remove('open');
      }
    });

    function fetchNotifs() {
      fetch('/api/notifications')
        .then(r => r.json())
        .then(items => {
          if (!items.length) {
            scroll.innerHTML = '<div class="notif-empty"><i class="bi bi-bell-slash d-block mb-2" style="font-size:1.8rem"></i>No notifications yet</div>';
            return;
          }
          scroll.innerHTML = items.map(n => `
            <a href="${n.link || '#'}"
               class="notif-row${n.is_read ? '' : ' unread'}">
              <div>${n.message}</div>
              <small style="color:var(--text-muted)">${n.time}</small>
            </a>
          `).join('');
        })
        .catch(() => {
          scroll.innerHTML = '<div class="notif-empty">Could not load notifications.</div>';
        });
    }

    if (markBtn) {
      markBtn.addEventListener('click', function () {
        fetch('/api/notifications/mark-read', {
          method: 'POST',
          headers: { 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/json' }
        })
        .then(() => {
          dot.classList.remove('show');
          scroll.querySelectorAll('.notif-row.unread')
                .forEach(el => el.classList.remove('unread'));
        })
        .catch(() => {});
      });
    }

    // Poll unread count every 45 s
    function pollCount() {
      fetch('/api/notifications/count')
        .then(r => r.json())
        .then(data => {
          if (data.count > 0) {
            dot.textContent = data.count > 9 ? '9+' : data.count;
            dot.classList.add('show');
          } else {
            dot.classList.remove('show');
          }
        })
        .catch(() => {});
    }
    pollCount();
    setInterval(pollCount, 45000);
  }

  /* ── 4. Smooth scroll for anchor links ───────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', function (e) {
      const t = document.querySelector(this.getAttribute('href'));
      if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth' }); }
    });
  });

  /* ── 5. Confirm dialogs for delete buttons ───────────────────── */
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm)) e.preventDefault();
    });
  });

});

/* ── Highlight matched text in suggestions ───────────────────── */
function highlight(text, query) {
  const re = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(re, '<strong style="color:var(--primary)">$1</strong>');
}

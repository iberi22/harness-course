/* === Harness Course — Shared Interactions v2 === */

document.addEventListener('DOMContentLoaded', function () {

  // ─── 1. Code Block Copy Buttons ───────────────────────────
  document.querySelectorAll('pre').forEach(function (pre) {
    var code = pre.querySelector('code');
    if (!code) return;
    var wrapper = document.createElement('div');
    wrapper.className = 'code-header';
    var btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = 'Copy';
    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(code.textContent || code.innerText || '').then(function () {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
      }).catch(function () { btn.textContent = 'Failed'; });
    });
    wrapper.appendChild(btn);
    pre.parentNode.insertBefore(wrapper, pre);
  });

  // ─── 2. Module Accordion (course.html) ────────────────────
  document.querySelectorAll('.module-collapsible').forEach(function (mod) {
    mod.addEventListener('click', function (e) {
      // Don't collapse when clicking links inside
      if (e.target.closest('a')) return;
      mod.classList.toggle('collapsed');
    });
  });

  // ─── 3. Sidebar Scrollspy ─────────────────────────────────
  var navLinks = document.querySelectorAll('.sidebar nav a[href*="/pages/"], .sidebar nav a[href*="/harness-course/pages/"]');
  if (navLinks.length > 0) {
    var sections = [];
    navLinks.forEach(function (link) {
      var href = link.getAttribute('href');
      // Extract the page name from href
      var pageName = href ? href.split('/').pop().replace('.html', '') : '';
      if (pageName) sections.push({ link: link, page: pageName });
    });

    // Check which page we're on
    var currentPath = window.location.pathname;
    sections.forEach(function (s) {
      if (currentPath.includes(s.page)) {
        navLinks.forEach(function (l) { l.classList.remove('active-nav'); });
        s.link.classList.add('active-nav');
      }
    });
  }

  // ─── 4. Sidebar Search ────────────────────────────────────
  var searchInput = document.getElementById('nav-search');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      var q = this.value.toLowerCase().trim();
      var links = document.querySelectorAll('.sidebar nav a');
      links.forEach(function (link) {
        var text = link.textContent.toLowerCase();
        if (!q || text.includes(q)) {
          link.style.display = 'flex';
        } else {
          link.style.display = 'none';
        }
      });
    });
  }

  // ─── 5. Keyboard shortcut: Cmd+K / Ctrl+K for search ──────
  document.addEventListener('keydown', function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      var searchEl = document.getElementById('nav-search');
      if (searchEl) searchEl.focus();
    }
  });

  // ─── 6. Smooth hash scrolling with offset ──────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});

(function () {
  const toggle = document.querySelector('.header__toggle');
  const nav = document.getElementById('site-nav');

  if (!toggle || !nav) return;

  const openNav = () => {
    nav.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('no-scroll'); // ⬅️ lock scroll body
    const firstLink = nav.querySelector('a, button');
    if (firstLink) firstLink.focus();
  };

  const closeNav = () => {
    nav.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('no-scroll'); // ⬅️ unlock scroll
    toggle.focus();
  };

  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    expanded ? closeNav() : openNav();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) closeNav();
  });

  document.addEventListener('click', (e) => {
    if (!nav.classList.contains('is-open')) return;
    const within = nav.contains(e.target) || toggle.contains(e.target);
    if (!within) closeNav();
  });
})();

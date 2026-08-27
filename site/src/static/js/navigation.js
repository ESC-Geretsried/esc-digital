(() => {
  const menu = document.querySelector('[data-mobile-menu]');
  if (!menu) return;

  menu.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      menu.open = false;
      menu.querySelector('summary')?.focus();
    }
  });

  menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    menu.open = false;
  }));

  document.addEventListener('click', (event) => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
})();

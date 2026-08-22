(() => {
  const root = document.querySelector('.hero-background[data-hero-images]');
  if (!root) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const images = (root.dataset.heroImages || '').split('|').filter(Boolean);
  const layers = Array.from(root.querySelectorAll('.hero-background__layer'));
  if (images.length < 2 || layers.length !== 2) return;

  let index = 0;
  let active = 0;
  const intervalMs = 7000;

  const preload = (src) => {
    const img = new Image();
    img.decoding = 'async';
    img.src = src;
  };

  preload(images[1]);

  window.setInterval(() => {
    index = (index + 1) % images.length;
    const nextLayer = 1 - active;
    const currentLayer = active;

    layers[nextLayer].style.backgroundImage = `url("${images[index]}")`;
    layers[nextLayer].classList.add('hero-background__layer--active');
    layers[currentLayer].classList.remove('hero-background__layer--active');
    active = nextLayer;

    preload(images[(index + 1) % images.length]);
  }, intervalMs);
})();

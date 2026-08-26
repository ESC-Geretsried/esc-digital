(() => {
  const root = document.querySelector('.hero-background');
  if (!root) return;

  const dayIndex = Math.floor(Date.now() / 86400000);
  const sources = Array.from(root.querySelectorAll('[data-hero-source]')).map((node) => {
    const dailyImages = (node.dataset.dailyImages || '').split('|').map((value) => value.trim()).filter(Boolean);
    const src = dailyImages.length ? dailyImages[dayIndex % dailyImages.length] : node.dataset.src;
    return {
      src,
      area: node.dataset.area || '',
      headline: node.dataset.headline || '',
      ctaLabel: node.dataset.ctaLabel || '',
      ctaPath: node.dataset.ctaPath || '#',
      focusDesktop: node.dataset.focusDesktop || '50% 50%',
      focusMobile: node.dataset.focusMobile || node.dataset.focusDesktop || '50% 50%'
    };
  }).filter((item) => item.src);

  const layers = Array.from(root.querySelectorAll('.hero-background__layer'));
  if (!sources.length || layers.length !== 2) return;

  const area = document.querySelector('[data-hero-area]');
  const headline = document.querySelector('[data-hero-headline]');
  const cta = document.querySelector('[data-hero-cta]');
  const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const mobile = () => window.matchMedia && window.matchMedia('(max-width: 650px)').matches;

  let index = 0;
  let active = 0;
  const intervalMs = 7000;

  const preload = (src) => {
    const img = new Image();
    img.decoding = 'async';
    img.src = src;
  };

  const applyMeta = (item) => {
    if (area) area.textContent = item.area;
    if (headline) headline.textContent = item.headline;
    if (cta) {
      cta.textContent = item.ctaLabel;
      cta.href = item.ctaPath;
    }
  };

  const setLayer = (layer, item) => {
    layer.style.backgroundImage = `url("${item.src}")`;
    layer.style.backgroundPosition = mobile() ? item.focusMobile : item.focusDesktop;
  };

  setLayer(layers[active], sources[0]);
  applyMeta(sources[0]);
  if (sources[1]) preload(sources[1].src);
  if (reducedMotion || sources.length < 2) return;

  window.setInterval(() => {
    index = (index + 1) % sources.length;
    const item = sources[index];
    const nextLayer = 1 - active;
    const currentLayer = active;

    setLayer(layers[nextLayer], item);
    layers[nextLayer].classList.add('hero-background__layer--active');
    layers[currentLayer].classList.remove('hero-background__layer--active');
    active = nextLayer;
    applyMeta(item);

    preload(sources[(index + 1) % sources.length].src);
  }, intervalMs);
})();

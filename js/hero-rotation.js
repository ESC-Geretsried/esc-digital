(() => {
  const GERETSRIED_TIME_ZONE = 'Europe/Berlin';

  const geretsriedDayIndex = (date = new Date()) => {
    const parts = Object.fromEntries(
      new Intl.DateTimeFormat('en-US', {
        timeZone: GERETSRIED_TIME_ZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }).formatToParts(date).filter((part) => part.type !== 'literal').map((part) => [part.type, part.value])
    );
    return Math.floor(Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day)) / 86400000);
  };

  const geretsriedWeekdayIndex = (date = new Date()) => {
    const weekday = new Intl.DateTimeFormat('en-US', {
      timeZone: GERETSRIED_TIME_ZONE,
      weekday: 'short'
    }).format(date);
    return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].indexOf(weekday);
  };

  const dailyImageFor = (dailyImages, date = new Date()) => (
    dailyImages.length ? dailyImages[geretsriedWeekdayIndex(date) % dailyImages.length] : null
  );

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      GERETSRIED_TIME_ZONE, geretsriedDayIndex, geretsriedWeekdayIndex,
      dailyImageFor
    };
  }
  if (typeof document === 'undefined') return;

  const root = document.querySelector('.hero-background');
  if (!root) return;

  const sources = Array.from(root.querySelectorAll('[data-hero-source]')).map((node) => {
    const dailyImages = (node.dataset.dailyImages || '').split('|').map((value) => value.trim()).filter(Boolean);
    return {
      src: dailyImageFor(dailyImages) || node.dataset.src,
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

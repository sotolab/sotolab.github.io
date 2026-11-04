'use strict';
(() => {
  if (window.__sotolabScrollInitialized) return;
  window.__sotolabScrollInitialized = true;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const active = new Set();
  const counters = new Map();
  const progress = document.createElement('div');
  progress.className = 's-reading-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  const backToTop = document.createElement('button');
  backToTop.type = 'button';
  backToTop.className = 's-back-to-top';
  backToTop.setAttribute('aria-label', '페이지 맨 위로 이동');
  backToTop.title = '맨 위로';
  backToTop.textContent = '↑';
  backToTop.hidden = true;
  backToTop.addEventListener('click', () => {
    document.querySelector('.s-logo')?.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: motion.matches ? 'auto' : 'smooth' });
  });
  document.body.append(backToTop);
  let scrollFrame = 0;
  function updateProgress() {
    scrollFrame = 0;
    const distance = document.documentElement.scrollHeight - window.innerHeight;
    const fraction = distance > 0 ? Math.max(0, Math.min(1, window.scrollY / distance)) : 0;
    progress.style.transform = `scaleX(${fraction})`;
    backToTop.hidden = window.scrollY < 400;
  }
  function scheduleProgress() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateProgress);
  }
  window.addEventListener('scroll', scheduleProgress, { passive: true });
  window.addEventListener('resize', scheduleProgress);
  updateProgress();

  if (!('IntersectionObserver' in window) || !Element.prototype.animate) return;

  function count(element) {
    const target = Number(element.dataset.countTo);
    if (!Number.isFinite(target) || target < 0) return;
    const original = element.textContent;
    const visual = document.createElement('span');
    visual.setAttribute('aria-hidden', 'true');
    const accessible = document.createElement('span');
    accessible.className = 's-sr-only';
    accessible.textContent = original;
    element.replaceChildren(visual, accessible);
    let start;
    const finish = () => {
      visual.textContent = original;
      counters.delete(element);
    };
    const state = { frame: 0, finish };
    counters.set(element, state);
    function tick(time) {
      if (motion.matches) { finish(); return; }
      start ??= time;
      const fraction = Math.min(1, (time - start) / 1600);
      const value = Math.floor(target * (1 - Math.pow(1 - fraction, 3)));
      visual.textContent = original.replace(/[\d,]+/, value.toLocaleString('ko-KR'));
      if (fraction < 1) state.frame = requestAnimationFrame(tick);
      else finish();
    }
    visual.textContent = original;
    state.frame = requestAnimationFrame(tick);
  }

  const selector = [
    '.s-section-heading', '.s-page-head h1', '.s-page-head > .s-wrap > p',
    '.s-card', '.s-course', '.s-step', '.s-book', '.s-record', '.s-fact',
    '.s-callout', '.s-content-title', '.s-split > div', '.s-person > div',
    '.s-quote', '.s-brand-lockup', '.s-logo-variant', '.s-company-history li',
    '.s-invite-steps li', '.s-cta .s-wrap', '.s-table tbody tr',
    '.e-hero-grid > div', '.e-intro', '.e-history-intro', '.e-history li',
    '.e-heading', '.e-case', '.e-product > *', '.e-teaching-feature > *',
    '.e-offerings > *', '.e-story-grid > *', '.e-contact .s-wrap',
    '.e-principles li', '.e-teaching-path li', '.page-title', '.page-description',
    '.section-header', '.core-card', '.sote-step', '.benefit-item',
    '.project-card', '.course-card', '.book-card', '.review-card',
    '.academy-course-card', '.academy-benefit-card', '.academy-simulator-card',
    '.academy-hero-visual', '.academy-summary-item', '.academy-curriculum-step',
    '.lecture-block', '.lecture-item', '.experience-item', '.faq-item', '.cta-inline',
    '.hero-copy', '.hero-visual', '.section-heading', '.program-card',
    '.kit-list article', '.product-image', '.timeline article', '.news-card',
    '.textbook', '.simulator', '.process-list li', '.faq-section details',
    '.contact-copy', '.inquiry-form', '[data-count-to]'
  ].join(',');

  const played = new WeakSet();
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      // A pixel-based trigger also works for cards taller than a phone screen.
      if (!entry.isIntersecting || played.has(entry.target)) return;
      const element = entry.target;
      played.add(element);
      observer.unobserve(element);
      if (motion.matches || document.hidden) return;
      if (element.hasAttribute('data-count-to')) { count(element); return; }
      const siblings = [...element.parentElement.children];
      const delay = Math.max(0, siblings.indexOf(element) % 3) * 65;
      // Animate only on entry: never leave content hidden while waiting to scroll.
      const animation = element.animate([
        { opacity: 0.6, transform: 'translateY(20px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 680, delay, easing: 'cubic-bezier(.22,.61,.36,1)' });
      active.add(animation);
      const cleanup = () => { active.delete(animation); };
      animation.onfinish = cleanup;
      animation.oncancel = cleanup;
    });
  }, { threshold: 0, rootMargin: '0px 0px -24px 0px' });

  function observeContent() {
    document.querySelectorAll(selector).forEach(element => {
      if (!played.has(element)) observer.observe(element);
    });
  }
  observeContent();
  // Filtering can reveal a previously hidden archive card.
  document.querySelectorAll('[data-archive-filter],#archive-reset,#archive-search').forEach(element => {
    element.addEventListener(element.id === 'archive-search' ? 'input' : 'click', observeContent);
  });
  motion.addEventListener('change', () => {
    if (!motion.matches) return;
    active.forEach(animation => animation.cancel());
    counters.forEach(state => { cancelAnimationFrame(state.frame); state.finish(); });
  });
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) return;
    active.forEach(animation => animation.finish());
    counters.forEach(state => { cancelAnimationFrame(state.frame); state.finish(); });
  });
})();

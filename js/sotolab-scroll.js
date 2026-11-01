'use strict';
(() => {
  if (!('IntersectionObserver' in window) || !Element.prototype.animate) return;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const active = new Set();
  const counters = new Map();
  const progress = document.createElement('div');
  progress.className = 's-reading-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  let scrollFrame = 0;
  function updateProgress() {
    scrollFrame = 0;
    const distance = document.documentElement.scrollHeight - window.innerHeight;
    const fraction = distance > 0 ? Math.max(0, Math.min(1, window.scrollY / distance)) : 0;
    progress.style.transform = `scaleX(${fraction})`;
  }
  function scheduleProgress() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateProgress);
  }
  window.addEventListener('scroll', scheduleProgress, { passive: true });
  window.addEventListener('resize', scheduleProgress);
  updateProgress();

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
    const finish = () => { visual.textContent = original; counters.delete(element); };
    const state = { frame: 0, finish };
    counters.set(element, state);
    function tick(time) {
      if (motion.matches) { finish(); return; }
      start ??= time;
      const fraction = Math.min(1, (time - start) / 1300);
      const value = Math.round(target * (1 - Math.pow(1 - fraction, 3)));
      visual.textContent = original.replace(/[\d,]+/, value.toLocaleString('ko-KR'));
      if (fraction < 1) state.frame = requestAnimationFrame(tick);
      else finish();
    }
    state.frame = requestAnimationFrame(tick);
  }

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      if (motion.matches) return;
      const element = entry.target;
      if (element.hasAttribute('data-count-to')) { count(element); return; }
      const animation = element.animate([
        { opacity: 0.35, transform: 'translateY(22px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 650, delay: Number(element.dataset.scrollDelay || 0), easing: 'cubic-bezier(.2,.7,.2,1)' });
      active.add(animation);
      animation.onfinish = animation.oncancel = () => active.delete(animation);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -25px 0px' });
  document.querySelectorAll('.s-section-heading,.s-card,.s-course,.s-step,.s-book,.s-record,.s-fact,.s-callout,.project-card').forEach(element => {
    const siblings = [...element.parentElement.children];
    element.dataset.scrollDelay = String(Math.min(siblings.indexOf(element) % 3, 2) * 70);
    observer.observe(element);
  });
  document.querySelectorAll('[data-count-to]').forEach(element => observer.observe(element));
  motion.addEventListener('change', () => {
    if (!motion.matches) return;
    active.forEach(animation => animation.cancel());
    counters.forEach(state => { cancelAnimationFrame(state.frame); state.finish(); });
  });
})();

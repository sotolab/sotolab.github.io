'use strict';
(() => {
  // The editorial palette uses a static background on every public page.
  if (document.body.matches('.story-page, .s-legacy-page')) return;
  if (document.getElementById('s-space-background')) return;
  const canvas = document.createElement('canvas');
  canvas.id = 's-space-background';
  canvas.setAttribute('aria-hidden', 'true');
  document.body.prepend(canvas);
  const ctx = canvas.getContext('2d');
  if (!ctx) { canvas.remove(); return; }

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let width = 0, height = 0, frame = 0, lastTime = 0, angle = 0;
  let pointerX = 0, pointerY = 0;
  const stars = Array.from({ length: 180 }, () => ({
    x: (Math.random() - 0.5) * 3,
    y: (Math.random() - 0.5) * 3,
    z: Math.random() * 2 + 0.2,
    size: Math.random() * 1.2 + 0.4
  }));
  const phi = (1 + Math.sqrt(5)) / 2;
  const vertices = [];
  for (const a of [-1, 1]) for (const b of [-phi, phi]) {
    vertices.push([0, a, b], [a, b, 0], [b, 0, a]);
  }
  const edges = [];
  vertices.forEach((v, i) => vertices.slice(i + 1).forEach((w, j) => {
    if (Math.abs(Math.hypot(...v.map((n, k) => n - w[k])) - 2) < 0.01) edges.push([i, i + j + 1]);
  }));

  function resize() {
    width = window.innerWidth; height = window.innerHeight;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (motion.matches || document.hidden) draw(0);
  }

  function draw(delta) {
    ctx.clearRect(0, 0, width, height);
    const glow = ctx.createRadialGradient(width * 0.75, height * 0.3, 0, width * 0.75, height * 0.3, width * 0.65);
    glow.addColorStop(0, 'rgba(110,65,185,0.19)'); glow.addColorStop(1, 'rgba(110,65,185,0)');
    ctx.fillStyle = glow; ctx.fillRect(0, 0, width, height);
    const scale = Math.max(width, height) * 0.65;
    stars.forEach(star => {
      star.z -= delta * 0.000035;
      if (star.z < 0.2) star.z += 2;
      const x = width / 2 + star.x * scale / star.z + pointerX * 12;
      const y = height / 2 + star.y * scale / star.z + pointerY * 12;
      ctx.fillStyle = `rgba(201,255,61,${Math.min(0.65, 0.75 / star.z)})`;
      ctx.fillRect(x, y, star.size / star.z, star.size / star.z);
    });
    angle += delta * 0.00011;
    const cy = Math.cos(angle), sy = Math.sin(angle), cx = Math.cos(angle * 0.4), sx = Math.sin(angle * 0.4);
    const size = Math.min(width * 0.27, height * 0.36, 290);
    const points = vertices.map(([x, y, z]) => {
      const rx = x * cy + z * sy, rz = z * cy - x * sy;
      const ry = y * cx - rz * sx, depth = y * sx + rz * cx;
      const perspective = 4 / (4 + depth);
      return [width * 0.68 + rx * size * perspective + pointerX * 20, height * 0.56 + ry * size * perspective + pointerY * 20];
    });
    ctx.strokeStyle = 'rgba(143,107,255,0.25)'; ctx.lineWidth = 1;
    ctx.beginPath();
    edges.forEach(([a, b]) => { ctx.moveTo(...points[a]); ctx.lineTo(...points[b]); });
    ctx.stroke();
  }

  function tick(time) {
    frame = 0;
    if (document.hidden || motion.matches) return;
    const delta = lastTime ? Math.min(time - lastTime, 50) : 0;
    lastTime = time; draw(delta);
    frame = requestAnimationFrame(tick);
  }
  function syncMotion() {
    cancelAnimationFrame(frame); frame = 0; lastTime = 0;
    draw(0);
    if (!document.hidden && !motion.matches) frame = requestAnimationFrame(tick);
  }
  window.addEventListener('resize', resize);
  window.addEventListener('pointermove', event => {
    pointerX = event.clientX / width - 0.5;
    pointerY = event.clientY / height - 0.5;
  }, { passive: true });
  document.addEventListener('visibilitychange', syncMotion);
  motion.addEventListener('change', syncMotion);
  resize(); syncMotion();
})();

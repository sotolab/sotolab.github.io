const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');

const root = join(__dirname, '..');
const source = readFileSync(join(root, 'js/sotolab-scroll.js'), 'utf8');

function setup({ width = 390, height = 640, reduced = false, supported = true } = {}) {
  const animations = [];
  const observed = new Set();
  const appended = [];
  const media = { matches: reduced, addEventListener: (_, fn) => { media.change = fn; } };
  class FakeElement {
    constructor() { this.style = {}; this.dataset = {}; this.textContent = ''; }
    setAttribute() {}
    addEventListener() {}
    hasAttribute(name) { return name === 'data-count-to' && this.dataset.countTo !== undefined; }
    animate(frames, options) {
      const animation = { frames, options, cancel() { this.cancelled = true; this.oncancel?.(); }, finish() { this.onfinish?.(); } };
      animations.push(animation);
      return animation;
    }
  }
  const target = new FakeElement();
  target.parentElement = { children: [target] };
  // A long mobile card must trigger without a minimum visible percentage.
  target.getBoundingClientRect = () => ({ top: 620, height: 2400 });
  let callback;
  let observerOptions;
  class Observer {
    constructor(fn, options) { callback = fn; observerOptions = options; }
    observe(element) { observed.add(element); }
    unobserve(element) { observed.delete(element); }
  }
  const window = {
    innerWidth: width, innerHeight: height, scrollY: 0,
    matchMedia: () => media, addEventListener() {}, scrollTo() {}
  };
  if (supported) window.IntersectionObserver = Observer;
  const document = {
    hidden: false, documentElement: { scrollHeight: 4000 },
    body: { append: element => appended.push(element) },
    createElement: () => new FakeElement(), querySelector: () => null,
    querySelectorAll: selector => selector.includes('.s-card') ? [target] : [],
    addEventListener() {}
  };
  const context = vm.createContext({
    window, document, Element: FakeElement, IntersectionObserver: Observer,
    requestAnimationFrame: () => 1, cancelAnimationFrame() {}, Set, Map, WeakSet
  });
  vm.runInContext(source, context);
  return {
    animations, observed, appended, media, target, observerOptions, context,
    enter: () => callback([{ target, isIntersecting: true, intersectionRatio: 0.001 }])
  };
}

test('phone: tall cards animate on entry, without hover or a percentage threshold', () => {
  const state = setup();
  assert.equal(state.observerOptions.threshold, 0);
  assert.equal(state.observerOptions.rootMargin, '0px 0px -24px 0px');
  assert.ok(state.observed.has(state.target));
  assert.equal(state.target.style.opacity, undefined);
  state.enter();
  assert.equal(state.animations.length, 1);
  assert.equal(state.animations[0].frames[1].opacity, 1);
  state.enter();
  assert.equal(state.animations.length, 1);
});

test('desktop uses the same entry animation as mobile', () => {
  const state = setup({ width: 1440, height: 900 });
  state.enter();
  assert.equal(state.animations.length, 1);
  assert.equal(state.animations[0].options.duration, 680);
});

test('reduced-motion preference keeps content visible and disables motion', () => {
  const state = setup({ reduced: true });
  state.enter();
  assert.equal(state.animations.length, 0);
  assert.equal(state.target.style.opacity, undefined);
});

test('enabling reduced motion cancels an active animation', () => {
  const state = setup();
  state.enter();
  state.media.matches = true;
  state.media.change();
  assert.equal(state.animations[0].cancelled, true);
});

test('unsupported animation environments retain readable content and top control', () => {
  const state = setup({ supported: false });
  assert.equal(state.target.style.opacity, undefined);
  assert.equal(state.appended.length, 2);
});

test('loading the script twice does not duplicate controls or animation', () => {
  const state = setup();
  vm.runInContext(source, state.context);
  assert.equal(state.appended.length, 2);
});

test('all 18 public pages load the current animation script exactly once', () => {
  const pages = ['index', 'profile', 'academy', 'academy-interior', 'academy-practice',
    'academy-special', 'academy-visit', 'academy-business', 'sotolab', 'experience',
    'books', 'contact', 'curriculum', 'mvp-projects', 'online', 'reviews', 'brand', 'history'];
  for (const page of pages) {
    const html = readFileSync(join(root, page + '.html'), 'utf8');
    assert.equal((html.match(/src="js\/sotolab-scroll\.js\?v=20261105-1"/g) || []).length, 1, page);
  }
});

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

test('desktop and mobile scroll motion preserves content and handles hidden tabs', async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    for (const width of [1440, 390, 320]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'no-preference' });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.addInitScript(() => {
        window.motionCalls = [];
        window.testHidden = false;
        Object.defineProperty(document, 'hidden', { get: () => window.testHidden });
        const animate = Element.prototype.animate;
        Element.prototype.animate = function (...args) {
          window.motionCalls.push({ className: this.className, text: this.textContent });
          return animate.apply(this, args);
        };
      });
      const visit = name => page.goto(pathToFileURL(path.resolve(__dirname, '..', name)).href);
      await visit('index.html');
      await page.waitForFunction(() => window.motionCalls.length > 0);
      await page.locator('.hero a[href="#inquiry"]').click();
      await page.waitForFunction(() => window.motionCalls.some(call => call.className === 'contact-copy'));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      assert.equal(new URL(page.url()).hash, '#inquiry');
      if (width < 500) {
        await page.locator('.s-back-to-top').click();
        await page.waitForFunction(() => scrollY === 0);
      }
      const landingDownload = page.locator('.hero a[download]');
      assert.match(await landingDownload.getAttribute('href'), /sotolab-education-guide\.pdf$/);
      await page.locator('footer nav a[href="brand-kit/guide.html"]').click();
      await page.waitForURL('**/brand-kit/guide.html');
      assert.equal(await page.locator('.hero a[download]').getAttribute('href'), 'sotolab-brand-kit.zip');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);

      await visit('sotolab.html');
      await page.locator('#mentor-story-title').scrollIntoViewIfNeeded();
      await page.waitForFunction(() => window.motionCalls.some(call => call.text === '오늘은 여기까지 왔네'));
      assert.equal(await page.locator('#mentor-story').count(), 1);

      await page.addInitScript(() => { window.testHidden = true; });
      await visit('profile.html');
      await page.waitForTimeout(150);
      assert.equal(await page.evaluate(() => window.motionCalls.length), 0);
      await page.evaluate(() => {
        window.testHidden = false;
        document.dispatchEvent(new Event('visibilitychange'));
      });
      await page.waitForFunction(() => window.motionCalls.length > 0);
      assert.deepEqual(errors, []);
      await page.close();
    }
    const reduced = await browser.newPage({ reducedMotion: 'reduce' });
    await reduced.goto(pathToFileURL(path.resolve(__dirname, '..', 'index.html')).href);
    await reduced.waitForTimeout(150);
    assert.equal(await reduced.evaluate(() => document.getAnimations().length), 0);
    assert.equal(await reduced.locator('h1').isVisible(), true);
    await reduced.close();
  } finally {
    await browser.close();
  }
});

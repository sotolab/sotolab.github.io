const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.argv[2] || 'playwright');

(async () => {
    const browser = await chromium.launch({ headless: true, channel: 'chrome' });
    try {
        for (const [name, size] of [['symbol', 256], ['app-icon', 512]]) {
            const page = await browser.newPage({ viewport: { width: size, height: size } });
            const asset = path.resolve(__dirname, '../brand-kit/assets', name);
            await page.goto(pathToFileURL(asset + '.svg').href);
            await page.screenshot({ path: asset + '.png', omitBackground: true });
            await page.close();
            console.log(`Rendered ${name}.png (${size}px)`);
        }
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });

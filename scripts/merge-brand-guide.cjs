const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.argv[2] || 'playwright');
const root = path.resolve(__dirname, '..');
(async () => {
    const browser = await chromium.launch({ headless: true, channel: 'chrome' });
    try {
        const page = await browser.newPage();
        const result = await page.evaluate(({ brand, guide, css }) => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(brand, 'text/html');
            const source = parser.parseFromString(guide, 'text/html');
            const main = source.querySelector('main');
            main.className = 'brand-guide';
            main.querySelector('h1').textContent = 'SotoLAB 브랜드 소개 · 브랜드킷';
            main.querySelector('.split').id = 'about';
            main.querySelectorAll('[src], [href]').forEach(node => {
                for (const attr of ['src', 'href']) {
                    const value = node.getAttribute(attr);
                    if (value && !/^(#|https?:|mailto:)/.test(value)) node.setAttribute(attr, 'brand-kit/' + value);
                }
            });
            const links = doc.createElement('div');
            links.className = 'guide-links';
            links.innerHTML = '<a href="#about">브랜드 소개</a><a href="#identity">로고 4종</a><a href="#colors">색상</a><a href="#voice">슬로건·철학</a><a href="#downloads">다운로드 ↓</a>';
            main.querySelector('.hero .wrap').prepend(links);
            for (const id of ['logo-variants', 'brand-kit']) {
                const anchor = doc.createElement('span'); anchor.id = id; main.querySelector('#identity').before(anchor);
            }
            doc.querySelector('main').replaceWith(main);
            doc.title = 'SotoLAB 브랜드 소개·브랜드킷 | Sunstar';
            doc.querySelectorAll('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]').forEach(node => node.content = 'Sunstar의 교육·멘토링 브랜드 SotoLAB. 브랜드 소개와 교육철학, 로고 4종, 색상·서체 가이드와 브랜드킷 다운로드를 한곳에서 확인하세요.');
            doc.querySelectorAll('meta[property="og:title"],meta[name="twitter:title"]').forEach(node => node.content = doc.title);
            if (!doc.querySelector('[href="css/brand-guide.css"]')) {
                for (const href of ['brand-kit/tokens.css', 'css/brand-guide.css']) {
                    const link = doc.createElement('link'); link.rel = 'stylesheet'; link.href = href; doc.head.append(link);
                }
                const script = doc.createElement('script'); script.src = 'brand-kit/guide.js'; script.defer = true; doc.head.append(script);
            }
            const sheet = new CSSStyleSheet(); sheet.replaceSync(css);
            // Scope guide rules to preserve the shared site header and footer.
            function scope(rules) {
                return [...rules].map(rule => {
                    if (rule.type === CSSRule.STYLE_RULE) {
                        const selectors = rule.selectorText.split(',').map(selector => {
                            const s = selector.trim();
                            return s === 'body' ? '.brand-guide' : s === 'html' ? 'html' : '.brand-guide ' + s;
                        }).join(',');
                        return selectors + '{' + rule.style.cssText + '}';
                    }
                    if (rule.cssRules) return rule.cssText.slice(0, rule.cssText.indexOf('{') + 1) + scope(rule.cssRules) + '}';
                    return rule.cssText;
                }).join('\n');
            }
            return { html: '<!DOCTYPE html>\n' + doc.documentElement.outerHTML + '\n', css: scope(sheet.cssRules) + '\n.brand-guide{font-family:var(--body-font);letter-spacing:0}.brand-guide h1,.brand-guide h2,.brand-guide h3{letter-spacing:0}.brand-guide .guide-links{display:flex;flex-wrap:wrap;gap:12px 24px;border-bottom:1px solid #526354;padding-bottom:24px;margin-bottom:28px;font-size:14px}.brand-guide .guide-links a{text-decoration:none}' };
        }, { brand: fs.readFileSync(path.join(root, 'brand.html'), 'utf8'), guide: fs.readFileSync(path.join(root, 'brand-kit/guide.html'), 'utf8'), css: fs.readFileSync(path.join(root, 'brand-kit/guide.css'), 'utf8') });
        fs.writeFileSync(path.join(root, 'brand.html'), result.html);
        fs.writeFileSync(path.join(root, 'css/brand-guide.css'), result.css);
        console.log('Integrated brand introduction and brand kit');
    } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });

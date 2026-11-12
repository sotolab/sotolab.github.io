const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.argv[2] || 'playwright');
const root = path.resolve(__dirname, '..');
const pages = {
    'index.html': ['장성균 박사 · 기술융합 서비스 개발과 교육 | SotoLAB', 'AI·IoT·블록체인·보안을 연결해 앱·웹 서비스를 기획하고 구현합니다. 장성균 박사의 개발·배포 경험을 실습 교육과 기업 멘토링으로 전합니다.'],
    'profile.html': ['장성균 박사 · 기술융합 개발자·교육자 | SotoLAB', 'AI·IoT·블록체인·보안을 연결하는 장성균 박사. 서비스 기획·설계·구현·배포 경험을 바탕으로 교육과 기업 멘토링을 진행합니다.'],
    'experience.html': ['기술융합 서비스·연구·교육 사례 | SotoLAB', 'AIoT 통합 플랫폼, 블록체인 서비스, NFC 보안 인증 등 장성균 박사의 기술융합 개발·연구와 교육 경험을 확인하세요.'],
    'academy.html': ['기술융합 실습·프로젝트 교육 | SotoLAB', 'AI·IoT·블록체인·보안을 앱·웹 서비스로 연결하는 실습 교육. 기획과 구현, 검증과 배포를 대상 수준에 맞춰 함께 배웁니다.']
};
(async () => {
    const browser = await chromium.launch({ headless: true, channel: 'chrome' });
    try {
        const page = await browser.newPage();
        for (const [name, [title, description]] of Object.entries(pages)) {
            const file = path.join(root, name);
            const snippets = Object.fromEntries(['profile', 'cases', 'education'].map(key => [key, fs.readFileSync(path.join(root, `data/fusion-${key}.html`), 'utf8')]));
            const html = await page.evaluate(({ text, name, title, description, snippets }) => {
                const doc = new DOMParser().parseFromString(text, 'text/html');
                doc.title = title;
                doc.querySelectorAll('meta[property="og:title"],meta[name="twitter:title"]').forEach(n => n.content = title);
                doc.querySelectorAll('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]').forEach(n => n.content = description);
                doc.querySelectorAll('script[type="application/ld+json"]').forEach(n => {
                    const data = JSON.parse(n.textContent);
                    if (data['@type'] === 'Person') {
                        data.jobTitle = '기술융합 서비스 개발자·교육자';
                        data.knowsAbout = ['인공지능', '사물인터넷', '블록체인', '정보보안', '앱·웹 서비스 개발', '기술 교육'];
                        n.textContent = JSON.stringify(data);
                    }
                });
                if (name === 'index.html') {
                    doc.querySelector('link[href*="sotolab-home.css"]').href = 'css/sotolab-home.css?v=20261112-1';
                } else if (name === 'profile.html') {
                    doc.querySelector('.s-page-head h1').innerHTML = '기술을 연결해 서비스를 만들고,<br>그 경험을 배움으로 전합니다';
                    doc.querySelector('.s-page-head p:not(.s-eyebrow)').textContent = '기술융합 서비스 개발자·교육자 장성균 박사 · AI·IoT·블록체인·보안을 연결하는 실무 경험을 직접 만드는 교육으로 전합니다.';
                    if (!doc.querySelector('#fusion')) doc.querySelector('#career').insertAdjacentHTML('beforebegin', snippets.profile);
                } else if (name === 'experience.html') {
                    if (!doc.querySelector('#fusion-cases')) doc.querySelector('#archive-results').insertAdjacentHTML('beforebegin', snippets.cases);
                } else if (name === 'academy.html') {
                    if (!doc.querySelector('#fusion-learning')) doc.querySelector('#teaching-approach').insertAdjacentHTML('afterend', snippets.education);
                    doc.querySelector('#academy-intro p:not(.s-eyebrow)').textContent = '기술을 따로 익히는 데서, 하나의 앱·웹 서비스를 직접 만드는 단계로. 대상과 수준에 맞춰 원리·연동·검증·배포를 함께 배웁니다.';
                }
                return '<!DOCTYPE html>\n' + doc.documentElement.outerHTML + '\n';
            }, { text: fs.readFileSync(file, 'utf8'), name, title, description, snippets });
            fs.writeFileSync(file, html);
        }
    } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });

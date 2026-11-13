'use strict';
(() => {
  const toggle = document.getElementById('brand-menu-toggle');
  const menu = document.getElementById('brand-menu');
  if (toggle && menu) {
    const groups = [...menu.querySelectorAll('.s-nav-group')];
    const closeGroups = except => groups.forEach(group => { if (group !== except) group.open = false; });
    const close = () => {
      closeGroups();
      menu.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.textContent = '메뉴';
    };
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      closeGroups();
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? '닫기' : '메뉴';
      menu.classList.toggle('is-open', open);
    });
    groups.forEach(group => {
      group.addEventListener('toggle', () => { if (group.open) closeGroups(group); });
    });
    menu.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
    document.addEventListener('click', event => {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) close();
    });
    document.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      const active = groups.find(group => group.open);
      if (active) {
        active.open = false;
        active.querySelector('summary').focus();
      } else if (toggle.getAttribute('aria-expanded') === 'true') {
        close(); toggle.focus();
      }
    });
    document.addEventListener('focusin', event => {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) close();
    });
  }
  const records = [...document.querySelectorAll('.s-record')];
  const archive = document.getElementById('archive-results');
  if (records.length && archive) {
    const categoryLinks = [...document.querySelectorAll('.s-archive-nav a[href^="?category="]')];
    const categoryLabels = new Map([['all', '전체 활동·경력'], ['career', '주요 경력']]);
    categoryLinks.forEach(link => {
      categoryLabels.set(new URL(link.href).searchParams.get('category'), link.textContent);
    });
    const patents = document.getElementById('archive-patents');
    const initial = new URLSearchParams(location.search).get('category');
    const category = patents && initial === 'patent' ? 'product' : categoryLabels.has(initial) ? initial : 'all';
    const credentials = document.getElementById('archive-credentials');
    const title = document.getElementById('archive-title');
    categoryLinks.find(link => new URL(link.href).searchParams.get('category') === category)
      ?.setAttribute('aria-current', 'page');
    const showPatents = category === 'all' || category === 'product';
    records.forEach(record => {
      record.hidden = category !== 'all' && record.dataset.category !== category
        && !(showPatents && record.dataset.category === 'patent');
    });
    if (title) title.textContent = categoryLabels.get(category);
    if (patents) patents.hidden = !showPatents;
    if (credentials) credentials.hidden = category !== 'product';
    // Category links land directly on the selected results.
    if (category !== 'all' || location.hash === '#archive-results') {
      requestAnimationFrame(() => {
        const target = document.getElementById(location.hash.slice(1));
        if (target?.classList.contains('s-record') && !target.hidden) {
          target.scrollIntoView({ block: 'start', behavior: 'auto' });
          return;
        }
        if (patents && initial === 'patent') {
          patents.scrollIntoView({ block: 'start', behavior: 'auto' });
          return;
        }
        archive.scrollIntoView({ block: 'start', behavior: 'auto' });
      });
    }
  }
  const form = document.getElementById('brand-inquiry');
  if (form) {
    const fields = document.getElementById('brand-inquiry-fields');
    if (fields) fields.disabled = false;
    const output = document.getElementById('brand-inquiry-summary');
    const status = document.getElementById('brand-copy-status');
    const update = () => {
      const data = new FormData(form);
      const value = key => String(data.get(key) || '').trim() || '협의 희망';
      output.value = `SotoLAB 교육·강연 및 멘토링 문의\n기관·담당자: ${value('organization')}\n문의 유형: ${value('type')}\n대상·인원: ${value('audience')}\n희망 일정: ${value('schedule')}\n교육 목표·관심 주제: ${value('goal')}`;
      status.textContent = '';
    };
    form.addEventListener('input', update);
    form.addEventListener('submit', async event => {
      event.preventDefault(); update();
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(output.value);
        status.textContent = '복사했습니다. 카카오톡 상담창이나 이메일에 붙여넣어 보내 주세요.';
      } catch {
        output.focus(); output.select();
        status.textContent = '문의 내용을 선택했습니다. 직접 복사해 카카오톡이나 이메일로 보내 주세요.';
      }
    });
    update();
  }
})();

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
  if (records.length) {
    const filters = [...document.querySelectorAll('[data-archive-filter]')];
    const search = document.getElementById('archive-search');
    const valid = new Set(filters.map(button => button.dataset.archiveFilter));
    const initial = new URLSearchParams(location.search).get('category');
    let category = valid.has(initial) ? initial : 'all';
    const titles = {
      all: '전체 활동 기록', education: '교육·강연 기록', mentoring: '멘토링 기록',
      research: '연구개발 기록', product: '개발 서비스 기록', patent: '특허·발명 기록'
    };
    const title = document.getElementById('archive-title');
    const update = () => {
      const query = search.value.trim().toLocaleLowerCase('ko');
      let count = 0;
      records.forEach(record => {
        const matches = (category === 'all' || record.dataset.category === category) && record.textContent.toLocaleLowerCase('ko').includes(query);
        record.hidden = !matches;
        if (matches) count++;
      });
      filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.archiveFilter === category)));
      if (title) title.textContent = titles[category];
      document.getElementById('archive-count').textContent = `${records.length}개 기록 중 ${count}개를 보고 있습니다.`;
      document.getElementById('archive-empty').hidden = count !== 0;
    };
    filters.forEach(button => button.addEventListener('click', () => { category = button.dataset.archiveFilter; update(); }));
    search.addEventListener('input', update);
    document.getElementById('archive-reset').addEventListener('click', () => { category = 'all'; search.value = ''; update(); search.focus(); });
    update();
    // Category links land directly on the selected results.
    if ((initial && valid.has(initial)) || location.hash === '#archive-results') {
      requestAnimationFrame(() => {
        document.getElementById('archive-results')?.scrollIntoView({ block: 'start', behavior: 'auto' });
        title?.focus({ preventScroll: true });
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

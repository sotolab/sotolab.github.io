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
  const search = document.getElementById('archive-search');
  if (records.length && search) {
    const categoryLinks = [...document.querySelectorAll('.s-archive-nav a[href^="?category="]')];
    const categoryLabels = new Map([['all', '전체 활동·경력'], ['career', '주요 경력']]);
    categoryLinks.forEach(link => {
      categoryLabels.set(new URL(link.href).searchParams.get('category'), link.textContent);
    });
    const year = document.getElementById('archive-year');
    const order = document.getElementById('archive-order');
    const patents = document.getElementById('archive-patents');
    const recordGrids = [...new Set(records.map(record => record.parentElement))];
    const initial = new URLSearchParams(location.search).get('category');
    const category = patents && initial === 'patent' ? 'product' : categoryLabels.has(initial) ? initial : 'all';
    const credentials = document.getElementById('archive-credentials');
    const title = document.getElementById('archive-title');
    categoryLinks.find(link => new URL(link.href).searchParams.get('category') === category)
      ?.setAttribute('aria-current', 'page');
    const update = () => {
      const query = search.value.trim().toLocaleLowerCase('ko');
      const selectedYear = year?.value || 'all';
      let count = 0;
      let patentCount = 0;
      records.forEach(record => {
        const { startYear, endYear } = record.dataset;
        const matchesYear = selectedYear === 'all' || (selectedYear === 'undated'
          ? Number(startYear) === 0
          : Number(startYear) <= Number(selectedYear) && Number(endYear) >= Number(selectedYear));
        const isPatent = record.dataset.category === 'patent';
        const matchesCategory = category === 'all' || record.dataset.category === category
          || (patents && category === 'product' && isPatent);
        const matches = matchesYear && matchesCategory
          && record.textContent.toLocaleLowerCase('ko').includes(query);
        record.hidden = !matches;
        if (matches) {
          count++;
          if (isPatent) patentCount++;
        }
      });
      if (title) title.textContent = categoryLabels.get(category);
      if (patents) patents.hidden = patentCount === 0;
      if (credentials) credentials.hidden = patents ? category !== 'product' : category !== 'patent';
      document.getElementById('archive-count').textContent = `${records.length}개 기록 중 ${count}개를 보고 있습니다.`;
      document.getElementById('archive-empty').hidden = count !== 0;
    };
    const sort = () => {
      if (!order) return;
      const direction = order.value === 'oldest' ? 1 : -1;
      const dated = direction === 1 ? 'startYear' : 'endYear';
      const ordered = [...records].sort((a, b) => {
        const left = Number(a.dataset[dated]);
        const right = Number(b.dataset[dated]);
        return !left || !right ? Number(!left) - Number(!right) : direction * (left - right);
      });
      recordGrids.forEach(grid => grid.append(...ordered.filter(record => record.parentElement === grid)));
    };
    search.addEventListener('input', update);
    year?.addEventListener('change', update);
    order?.addEventListener('change', sort);
    document.getElementById('archive-reset').addEventListener('click', () => {
      search.value = '';
      if (year) year.value = 'all';
      if (order) order.value = 'newest';
      sort();
      update();
      search.focus();
    });
    update();
    const controls = document.getElementById('archive-controls');
    if (controls) controls.hidden = false;
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

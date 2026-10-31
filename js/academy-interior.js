'use strict';
const scenes = {
  study: { title: '집중하는 시간,<br>또렷한 빛으로', status: '밝은 조명 · 학습 장면' },
  rest: { title: '머무는 순간,<br>공간이 달라집니다.', status: '따뜻한 조명 · 휴식 장면' },
  away: { title: '떠난 자리,<br>조명도 쉬어갑니다.', status: '조명 OFF · 외출 장면' }
};
document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => {
  const mode = button.dataset.mode;
  document.querySelector('.hero-visual').dataset.scene = mode;
  document.querySelectorAll('[data-mode]').forEach(item => {
    const selected = item === button;
    item.classList.toggle('selected', selected);
    item.setAttribute('aria-pressed', String(selected));
  });
  document.getElementById('scene-title').innerHTML = scenes[mode].title;
  document.getElementById('scene-status').textContent = scenes[mode].status;
}));
const simulator = {
  '3d': { image: 'academy-simulator-3d.png', alt: 'IoTPlacement 3D 공간 시뮬레이션 예시', caption: '공간 안에서 장치와 조명 배치를 입체적으로 이해합니다.' },
  plan: { image: 'academy-simulator-plan.png', alt: 'IoTPlacement 평면 배치 시뮬레이션 예시', caption: '평면 구조를 기준으로 공간과 장치의 위치 관계를 살펴봅니다.' },
  light: { image: 'academy-simulator-lighting-example.png', alt: 'IoTPlacement 조명 설정 예시', caption: '시뮬레이터의 조명 예시를 보며 공간 적용 방향을 생각합니다.' }
};
document.querySelectorAll('[data-sim]').forEach(button => button.addEventListener('click', () => {
  const data = simulator[button.dataset.sim];
  const img = document.getElementById('sim-img');
  img.src = 'img/' + data.image;
  img.alt = data.alt;
  document.getElementById('sim-caption').textContent = data.caption;
  document.querySelectorAll('[data-sim]').forEach(item => {
    item.classList.toggle('active', item === button);
    item.setAttribute('aria-pressed', String(item === button));
  });
}));
const form = document.getElementById('inquiry-form');
const summary = document.getElementById('inquiry-summary');
function updateInquiry() {
  const data = new FormData(form);
  const school = String(data.get('school') || '').trim() || '미정';
  const department = String(data.get('department') || '').trim() || '미정';
  const schedule = String(data.get('schedule') || '').trim() || '협의 희망';
  const rawPeople = Number(data.get('people'));
  const validPeople = Number.isInteger(rawPeople) && rawPeople >= 1 && rawPeople <= 1000;
  const peopleText = validPeople ? `${rawPeople}명` : '협의 희망';
  const cohorts = validPeople ? Math.ceil(rawPeople / 15) : 1;
  document.getElementById('cohort-note').textContent = cohorts > 1
    ? `총 ${rawPeople}명은 실습 최대 15명 기준 최소 ${cohorts}개 분반·회차를 협의합니다.`
    : '실습교육 1회 최대 15명 기준입니다.';
  summary.value = `대학 연계 IoT 공간디자인 교육 도입 문의\n학교·기관: ${school}\n학과·대상: ${department}\n참여 예정: ${peopleText}\n희망 일정: ${schedule}\n구성: 교육키트 + 학생 실습교육(4시간·최대 15명/회) + 학기 중 2시간 특강 + 캡스톤 멘토링\n키트 수량, 일정 및 통합 견적 상담을 희망합니다.`;
  document.getElementById('copy-status').textContent = '';
}
form.addEventListener('input', updateInquiry);
form.addEventListener('submit', async event => {
  event.preventDefault();
  updateInquiry();
  const status = document.getElementById('copy-status');
  try {
    if (!navigator.clipboard?.writeText) throw new Error('clipboard unavailable');
    await navigator.clipboard.writeText(summary.value);
    status.textContent = '복사했습니다. 상담창을 열어 문의 내용을 붙여넣어 주세요.';
  } catch {
    summary.focus();
    summary.select();
    status.textContent = '문의 내용을 선택했습니다. 복사한 뒤 상담창에 붙여넣어 주세요.';
  }
});
updateInquiry();
document.getElementById('print-page').addEventListener('click', () => window.print());

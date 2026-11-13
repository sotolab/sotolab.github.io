"""Build the two-page SotoLAB overview for education coordinators."""
from pathlib import Path
from runpy import run_path


def main():
    # Reuse the brochure typography, palette and page layout primitives.
    source = run_path(str(Path(__file__).with_name('build-education-guide.py')))
    guide = source['Guide'](
        source['ROOT'] / 'output/pdf/sotolab-institution-overview.pdf',
        'SotoLAB · 기관용 맞춤 실습교육 안내',
    )
    forest, paper, muted, clay = (source[key] for key in ('FOREST', 'PAPER', 'MUTED', 'CLAY'))
    site = source['SITE']
    margin, width = source['M'], source['CONTENT']

    guide.start('SotoLAB  /  기관용 교육 안내')
    guide.paragraph('현장의 과제로,\n수업을 만듭니다', 88, size=42, leading=54,
                    font='Display', color=forest)
    guide.paragraph('장성균 공학박사 · 썬스타의 교육·멘토링 브랜드 SotoLAB',
                    212, size=12, bold=True, color=clay)
    guide.paragraph('교육 대상과 현장의 과제를 먼저 살펴보고, 교육 시간과 참여자의 경험에 맞춰 실습과 결과물의 범위를 정합니다.',
                    248, size=12, leading=20, color=muted)
    for i, (audience, title, detail, result) in enumerate([
        ('기업·공공기관', '생성형 AI 업무 적용',
         '보고서·회의록 초안, 사내 문서 질의응답, AI 결과의 근거와 검토 기준',
         '맞춤 특강 · 실습 워크숍 · 팀 멘토링'),
        ('대학·교육기관', 'AI 앱·웹 개발과 기술융합',
         'AI 기능 구현과 API 연동, 과제에 맞춘 IoT·블록체인·정보보안 실습',
         '실습 특강 · 프로젝트 수업 · 캡스톤 자문'),
        ('창업팀·프로젝트팀', '서비스 기획과 기술 멘토링',
         '문제 정의, 핵심 기능 선정, 시제품 설계와 검증 계획',
         '과제별 기술 자문 · 프로젝트 멘토링'),
    ]):
        top = 326 + i * 124
        guide.rule(top)
        guide.paragraph(audience, top + 13, size=10, bold=True, color=clay)
        guide.paragraph(title, top + 37, size=20, leading=26, font='Display', color=forest)
        guide.paragraph(detail, top + 71, size=10.5, color=muted)
        guide.paragraph(result, top + 96, size=9.5, bold=True, color=forest)
    guide.link('웹에서 대상별 교육 과정 보기', 721, site + '#classes')

    guide.start('SotoLAB  /  대표 이력과 교육 문의')
    guide.paragraph('직접 해온 경험을,\n함께 해내는 배움으로', 85, size=34, leading=46,
                    font='Display', color=forest)
    records = [
        ('강의', '한컴아카데미 AI·IoT 전문 과정 개발·강의, 가톨릭대 AIoT 실습 특강', 'education'),
        ('프로젝트', '한국전자통신연구원 달 탐사 통신 과제 참여, 블록체인 통합 모듈 개발', 'research'),
        ('멘토링', '대학생 IT 프로젝트, 광주정보문화산업진흥원 청년 ICT 기술 멘토링', 'mentoring'),
        ('서비스', '에코브리티 플랫폼 개발·서비스 관리, 입찰비서 개발·운영', 'product'),
        ('학위·특허', '컴퓨터소프트웨어 전공 공학박사, BLE 무선 장치 제어 특허 등록 이력', 'patent'),
    ]
    for i, (label, detail, category) in enumerate(records):
        top = 203 + i * 49
        guide.rule(top)
        guide.link(label, top + 10, site + f'experience.html?category={category}#archive-results',
                   width=75)
        guide.paragraph(detail, top + 10, x=137, width=404, size=10.5, leading=16, color=muted)
    guide.box(margin, 481, width, 216, forest)
    guide.paragraph('교육 문의부터 진행까지', 502, x=margin + 19, width=width - 38,
                    size=19, font='Display', color=paper)
    guide.paragraph('문의 → 목표와 현장 확인 → 커리큘럼·일정 확정 → 교육 진행', 543,
                    x=margin + 19, width=width - 38, size=10.5, bold=True, color=paper)
    guide.paragraph('교육 대상과 인원, 해보고 싶은 과제, 희망 일정을 알려주세요.', 574,
                    x=margin + 19, width=width - 38, size=10, color=paper)
    guide.link('카카오톡으로 문의', 620, 'https://open.kakao.com/o/sK8hYXfb',
               x=margin + 19, width=145, dark=True)
    guide.link('sotolabedu@gmail.com', 620, 'mailto:sotolabedu@gmail.com',
               x=margin + 174, width=235, dark=True)
    guide.link('홈페이지 문의 구역', 651, site + '#inquiry', x=margin + 19,
               width=220, dark=True)
    guide.link('활동·경력 전체 보기', 735, site + 'experience.html')
    guide.pdf.save()


if __name__ == '__main__':
    main()

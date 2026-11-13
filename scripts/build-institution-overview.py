"""Build the SotoLAB education catalog for institutional buyers."""
from pathlib import Path
from runpy import run_path


def main():
    source = run_path(str(Path(__file__).with_name('build-education-guide.py')))
    guide = source['Guide'](
        source['ROOT'] / 'output/pdf/sotolab-institution-overview.pdf',
        'SotoLAB · 맞춤 실습교육 카탈로그',
    )
    forest, paper, muted, clay, sage, warm = (
        source[key] for key in ('FOREST', 'PAPER', 'MUTED', 'CLAY', 'SAGE', 'WARM')
    )
    site = source['SITE']
    margin, width, page_width = (source[key] for key in ('M', 'CONTENT', 'W'))

    guide.start(dark=True)
    logo = source['ROOT'] / 'brand-kit/assets/logo-dark.png'
    guide.pdf.drawImage(str(logo), margin - 8, source['H'] - 78, width=113, height=38,
                        mask=[0, 18, 0, 18, 0, 18])
    guide.paragraph('SotoLAB 맞춤 실습교육 카탈로그', 52, x=345, width=196,
                    size=10, color=sage)
    guide.paragraph('우리 일에 바로 써볼\n도구 하나', 102, size=45, leading=57,
                    font='Display', color=paper)
    guide.paragraph('팀의 반복 업무를 실습 과제로 삼아, 결과를 검토하고\n다시 써볼 수 있는 도구를 만듭니다.',
                    232, size=13, leading=22, color=sage)
    guide.photograph(source['AI_DESK'], 0, 304, page_width, 365, focus=.55)
    guide.paragraph('직접 해온 경험을, 함께 해내는 배움으로', 707, size=16,
                    font='Display', color=paper)
    guide.paragraph('장성균 공학박사 · 기업·공공기관 · 대학·교육기관 · 프로젝트팀',
                    756, size=10, color=warm)

    guide.start('기업·공공기관  /  생성형 AI 업무 적용')
    guide.word_wrap = None
    guide.paragraph('보고서 초안부터\n팀이 다시 쓰는 도구까지', 91, size=35, leading=46,
                    font='Display', color=forest)
    guide.paragraph('매주 여러 자료를 열어 진행 상황을 옮기는 업무를 실습에 가져옵니다. 팀이 쓰는 양식에 맞춰 초안을 만들고, 빠진 정보는 검토 항목으로 표시합니다.',
                    203, size=12, leading=21, color=muted)
    guide.box(margin, 290, width, 245, forest)
    guide.paragraph('실습 결과물 예시', 311, x=margin + 20, width=width - 40,
                    size=10, bold=True, color=warm)
    guide.paragraph('주간 업무보고 초안', 343, x=margin + 20, width=width - 40,
                    size=26, font='Display', color=paper)
    for i, (label, value) in enumerate([
        ('진행 현황', '시제품 검토 완료 · 회의 기록 2쪽'),
        ('다음 할 일', '시험 일정 확정 · 일정표 1쪽'),
        ('담당자 확인', '완료 예정일이 자료에 없어 확인 필요'),
    ]):
        top = 399 + i * 37
        guide.box(margin + 20, top - 6, width - 40, .5, sage)
        guide.paragraph(label, top, x=margin + 20, width=90, size=10, bold=True, color=warm)
        guide.paragraph(value, top, x=margin + 113, width=width - 135, size=11, color=paper)
    for i, (title, detail) in enumerate([
        ('반복 작업 줄이기', '자료를 옮겨 적는 시간을 줄일 수 있는지 기존 방식과 비교합니다.'),
        ('검토 기준 공유', '근거와 확인 항목을 남겨 동료도 같은 기준으로 결과를 검토할 수 있습니다.'),
        ('다음 업무에 적용', '새 자료를 넣어 다시 실행하고 어떤 부분을 바꿔야 하는지 설명합니다.'),
    ]):
        x = margin + i * 166
        guide.paragraph(title, 585, x=x, width=152, size=15, font='Display', color=clay)
        guide.paragraph(detail, 626, x=x, width=146, size=10.5, leading=18, color=muted)
    guide.paragraph('다른 실습 주제  /  회의록 후속 작업 정리 · 사내 규정 질의응답',
                    747, size=10, bold=True, color=forest)

    guide.start('대학·교육기관과 프로젝트팀  /  구현과 검증')
    guide.word_wrap = None
    guide.paragraph('아이디어를 설명하는 데서\n작동을 보여주는 데까지', 91, size=34, leading=46,
                    font='Display', color=forest)
    for i, (audience, title, detail, benefit) in enumerate([
        ('대학·교육기관', '시연 가능한 AI 앱·웹',
         'AI 기능을 앱이나 웹에 연결하고, 답변에 근거를 표시하거나 실패했을 때 안내하는 동작을 만듭니다. 과제에 따라 IoT·블록체인·정보보안을 함께 다룹니다.',
         '수업 후 · 무엇을 구현했고 어떤 조건에서 동작하는지 시연하고 설명'),
        ('창업팀·프로젝트팀', '검증할 기능이 분명한 시제품',
         '사용자가 겪는 문제에서 출발해 핵심 기능 하나를 고릅니다. 필요한 기술과 개발 순서를 정하고, 무엇을 확인해야 다음 단계로 갈 수 있는지 계획합니다.',
         '수업 후 · 무엇부터 개발할지 팀이 합의하고 다음 실험을 시작'),
    ]):
        top = 223 + i * 188
        guide.rule(top)
        guide.paragraph(audience, top + 13, size=10, bold=True, color=clay)
        guide.paragraph(title, top + 41, size=23, font='Display', color=forest)
        guide.paragraph(detail, top + 88, size=11.5, leading=20, color=muted)
        guide.paragraph(benefit, top + 145, size=10.5, bold=True, color=forest)
    guide.box(margin, 625, width, 123, forest)
    guide.paragraph('교육 시간에 맞춘 결과물', 645, x=margin + 19, width=width - 38,
                    size=17, font='Display', color=paper)
    guide.paragraph('특강은 핵심 동작 하나를 직접 확인합니다. 워크숍은 자기 과제에 적용하고, 프로젝트 과정은 시제품 검증과 피드백까지 이어갑니다.',
                    685, x=margin + 19, width=width - 38, size=11, leading=18, color=paper)

    guide.start('SotoLAB  /  실무 경험이 수업이 되는 과정')
    guide.word_wrap = None
    guide.paragraph('직접 해본 일에서\n수업에 필요한 판단을 고릅니다', 88, size=32, leading=44,
                    font='Display', color=forest)
    for i, (label, evidence, connection, category) in enumerate([
        ('강의', '한컴아카데미 AI·IoT 과정 개발과 강의',
         '참여자의 수준에 맞춰 개념 설명과 실습 순서를 조정합니다.', 'education'),
        ('프로젝트', '달 탐사 통신 과제 참여 · 블록체인 통합 모듈 개발',
         '각 기술의 역할을 이해하고 연결 지점의 실패 조건을 살핍니다.', 'research'),
        ('서비스', '에코브리티 플랫폼 개발·관리 · 입찰비서 개발·운영',
         '사용자가 실제로 하는 일을 기준으로 기능과 검증 범위를 고릅니다.', 'product'),
        ('멘토링', '대학생 IT 프로젝트 · 청년 ICT 기술 멘토링',
         '스스로 해결할 수 있도록 과제를 나누고 다음 시도를 함께 정합니다.', 'mentoring'),
    ]):
        top = 209 + i * 84
        guide.rule(top)
        guide.link(label, top + 12, site + f'experience.html?category={category}#archive-results', width=75)
        guide.paragraph(evidence, top + 12, x=137, width=404, size=10.5, bold=True, color=forest)
        guide.paragraph(connection, top + 39, x=137, width=404, size=10.5, leading=17, color=muted)
    guide.box(margin, 565, width, 148, forest)
    guide.paragraph('“마지막에는 주어진 업무도 해내는\n나를 볼 수 있었다.”', 589, x=margin + 20,
                    width=width - 40, size=20, leading=30, font='Serif', color=paper)
    guide.paragraph('첫 IT 인턴십에 참여한 멘티의 소감', 674, x=margin + 20,
                    width=width - 40, size=9.5, color=warm)
    guide.link('소토랩 교육 과정 살펴보기', 740, site + '#classes')
    guide.paragraph('표지 사진은 교육 맥락을 표현한 연출 이미지입니다.', 770,
                    size=8, color=muted)
    guide.pdf.save()


if __name__ == '__main__':
    main()

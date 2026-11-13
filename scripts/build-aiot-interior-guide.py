"""Build the university AIoT course guide from the published academy program."""
from pathlib import Path
from runpy import run_path


def main():
    shared = run_path(str(Path(__file__).with_name('build-education-guide.py')))
    root, site = shared['ROOT'], shared['SITE']
    guide = shared['Guide'](
        root / 'output/pdf/sotolab-aiot-interior-course.pdf',
        'SotoLAB · AIoT 스마트홈 인테리어 대학 특강',
    )
    forest, paper, sage, muted, clay = (shared[key] for key in ('FOREST', 'PAPER', 'SAGE', 'MUTED', 'CLAY'))
    margin, width = shared['M'], shared['CONTENT']
    course = shared['tree']('academy-interior.html')
    plain = shared['plain']

    guide.start(dark=True)
    guide.paragraph('SotoLAB', 45, size=18, bold=True, color=sage)
    guide.paragraph('AIoT 스마트홈 인테리어\n대학 특강', 99, size=34, leading=45, font='Display', color=paper)
    guide.paragraph('학생이 설계한 공간이 빛과 센서에 반응하도록 직접 구현하는 맞춤 실습교육',
                    211, size=13, color=sage)
    guide.photograph(root / 'img/academy-simulator-3d.png', 0, 272, shared['W'], 315)
    guide.paragraph('IoTPlacement 공간 설계 시뮬레이션', 600, size=9, color=sage)
    guide.paragraph('학생 실습 4시간  /  1회 최대 15명  /  학기 중 특강 2시간',
                    647, size=12, bold=True, color=paper)
    guide.paragraph('실내건축·실내디자인·주거환경·공간디자인 전공과 융합 프로젝트를 위한 과정',
                    686, size=11, color=sage)
    guide.link('가톨릭대학교 특강 운영 사례 보기', 742, shared['UNIVERSITY'], dark=True)

    guide.start('SotoLAB  /  대학 연계 AIoT 교육')
    guide.paragraph('4시간 학생 실습 커리큘럼', 90, size=29, font='Display', color=forest)
    guide.paragraph('장치를 연결하고, 공간에 어울리는 조명 장면을 만든 뒤, 센서 조건으로 조명이 작동하는지 직접 검증합니다.',
                    150, size=12, color=muted)
    for index, row in enumerate(course.xpath('//div[@class="timeline"]/article')):
        top = 215 + index * 115
        guide.rule(top)
        time = row.xpath('./div[@class="time"]/text()')[0].strip().replace('–', ' - ')
        guide.paragraph(time, top + 13, size=10, width=105, bold=True, color=clay)
        x = margin + 117
        body_width = width - 117
        guide.paragraph(plain(row.xpath('.//h3')[0]), top + 11, x=x, width=body_width, size=15, bold=True)
        guide.paragraph(plain(row.xpath('.//p')[0]), top + 40, x=x, width=body_width, size=10, color=muted)
        guide.paragraph(plain(row.xpath('.//span[@class="outcome"]')[0]), top + 78, x=x,
                        width=body_width, size=10, bold=True, color=forest)

    guide.box(margin, 685, width, 83, sage)
    guide.paragraph('실습 준비', 696, x=margin + 15, size=11, bold=True)
    guide.paragraph('스마트폰과 제어 앱, 연결 가능한 네트워크, 전원과 실습 공간\n학과 인원에 맞춘 키트 수량과 조 편성',
                    719, x=margin + 15, width=width - 30, size=10, color=muted)

    guide.start('SotoLAB  /  대학 연계 AIoT 교육')
    guide.paragraph('특강·캡스톤 연계와 교육비', 90, size=29, font='Display', color=forest)
    guide.paragraph('학기 중 하루 2시간 특강', 155, size=15, bold=True, color=forest)
    for index, topic in enumerate(course.xpath('//*[@id="lecture"]//li')):
        title, detail = (plain(topic.xpath(f'.//{tag}')[0]) for tag in ('h3', 'p'))
        guide.paragraph(f'{title} · {detail}', 190 + index * 27, size=10.5, color=muted)

    guide.rule(276)
    guide.paragraph('교육 키트와 캡스톤 멘토링', 297, size=15, bold=True, color=forest)
    guide.paragraph('아카라 홈키트, RGB 전구, 스탠드 조명, 조명 소켓으로 실습을 구성합니다. 캡스톤과 연계할 때는 사용자와 공간 문제를 정리하고, 기기 배치와 자동화 조건, 검증 기준을 함께 구체화합니다.',
                    332, size=11, color=muted)

    guide.box(margin, 432, width, 232, sage)
    x = margin + 20
    guide.paragraph('교육비  /  구성별 통합 견적', 449, x=x, size=16, bold=True, color=forest)
    guide.paragraph('실습 4시간과 학기 중 특강 2시간을 기준으로, 아래 항목을 확정해 견적을 산정합니다.',
                    489, x=x, width=width - 40, size=11, color=muted)
    guide.paragraph('강의 운영 · 참여 인원, 실습 분반·추가 회차, 교육 장소\n실습 장비 · 키트 수량, 개인·팀별 구성과 공급 조건\n연계 항목 · 캡스톤 멘토링 범위, 교재와 IoTPlacement 이용 조건\n부대 비용 · 출장 등 현장 운영 조건에 따른 비용',
                    535, x=x, width=width - 40, size=10.5, leading=24, color=forest)
    guide.paragraph('실습 인원이 15명을 넘으면 분반이나 추가 회차를 협의합니다. 2시간 특강의 인원은 강의 공간과 진행 방식에 맞춰 정합니다.',
                    688, size=10.5, color=muted)
    guide.link('대학 연계 교육 상세 페이지 보기', 753, site + 'academy-interior.html#program')
    guide.pdf.save()


if __name__ == '__main__':
    main()

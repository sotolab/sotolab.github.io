"""Build the public SotoLAB education PDF from the site's published records."""
import json
import os
from pathlib import Path
import re
import subprocess
from xml.sax.saxutils import escape

from lxml import html
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output/pdf/sotolab-education-guide.pdf'
HISTORY = '3636d6ab4c30f0a4865d4ad8af44cdb767ca4b6c'
SITE = 'https://sotolab.github.io/'
UNIVERSITY = 'https://www.catholic.ac.kr/ko/newsroom/photonews.do?mode=view&articleNo=274897'
INQUIRY = SITE + '#inquiry'
FONT_DIR = Path(os.environ.get('SOTOLAB_PDF_FONT_DIR', 'C:/Windows/Fonts'))
W, H = A4
M = 54
CONTENT = W - 2 * M
FOREST = HexColor('#172e22')
GREEN = HexColor('#315641')
SAGE = HexColor('#c9ddc0')
INK = HexColor('#101b14')
MUTED = HexColor('#4e6053')
PAPER = HexColor('#f8f6ef')
TINT = HexColor('#e6eee0')
LINE = HexColor('#c7d1c4')
PHOTO = ROOT / 'img/academy-simulator-3d.png'
PLAN = ROOT / 'img/academy-simulator-plan.png'

for name, filename in [('KR', 'malgun.ttf'), ('KR-Bold', 'malgunbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))


def tree(name):
    return html.fromstring((ROOT / name).read_text(encoding='utf-8-sig'))


def plain(node):
    return ' '.join(''.join(node.itertext()).split())


def excerpts():
    old_html = subprocess.check_output(['git', 'show', f'{HISTORY}:review.html'], cwd=ROOT)
    archive = html.fromstring(old_html.decode('utf-8'))
    reviews = [(plain(card.xpath('.//h6')[0]), plain(card.xpath('./p')[0]))
               for card in archive.xpath('//div[@class="testimonial-box"]')]
    assert len(reviews) == 14 and all(len(body) > 500 for _, body in reviews)
    return reviews


class Guide:
    def __init__(self):
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        self.pdf = Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
        self.pdf.setTitle('SotoLAB 브랜드 소개 및 프로젝트 교육 안내')
        self.pdf.setAuthor('SotoLAB · Sunstar')
        self.page = 0
        self.y = 0

    def box(self, x, top, width, height, color):
        self.pdf.setFillColor(color)
        self.pdf.rect(x, H - top - height, width, height, fill=1, stroke=0)

    def rule(self, top, color=LINE):
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(.7)
        self.pdf.line(M, H - top, W - M, H - top)

    def paragraph(self, value, top, *, x=M, width=CONTENT, size=12, leading=None, bold=False,
                  color=INK, draw=True):
        style = ParagraphStyle(
            'guide', fontName='KR-Bold' if bold else 'KR', fontSize=size,
            leading=leading or size * 1.62, textColor=color, alignment=TA_LEFT, wordWrap='CJK')
        rendered = Paragraph(escape(value).replace('\n', '<br/>'), style)
        _, height = rendered.wrap(width, H)
        if draw:
            if top + height > H - 49:
                raise ValueError(f'Page {self.page} overflow at {top + height:.1f}: {value[:45]}')
            rendered.drawOn(self.pdf, x, H - top - height)
        return height

    def text(self, value, *, size=12, leading=None, gap=14, color=INK, bold=False, width=CONTENT):
        self.y += self.paragraph(value, self.y, width=width, size=size,
                                 leading=leading, color=color, bold=bold) + gap

    def start(self, label, *, dark=False):
        if self.page:
            self.pdf.showPage()
        self.page += 1
        self.box(0, 0, W, H, FOREST if dark else PAPER)
        accent = SAGE if dark else GREEN
        self.paragraph(label, 39, size=10, bold=True, color=accent)
        self.rule(61, HexColor('#597660') if dark else LINE)
        self.rule(H - 46, HexColor('#597660') if dark else LINE)
        self.pdf.setFont('KR', 8)
        self.pdf.setFillColor(accent)
        self.pdf.drawString(M, 28, 'SotoLAB  /  프로젝트 교육 안내')
        self.pdf.drawRightString(W - M, 28, str(self.page).zfill(2))
        self.y = 90

    def chapter(self, key, label, title, intro=None):
        self.start(label)
        self.pdf.bookmarkPage(key)
        self.pdf.addOutlineEntry(title, key, level=0)
        self.text(title, size=29, leading=39, bold=True, gap=17, color=FOREST)
        if intro:
            self.text(intro, size=12, gap=22, color=MUTED)

    def link(self, value, top, url, *, x=M, width=CONTENT, dark=False, internal=False):
        height = self.paragraph(value, top, x=x, width=width, size=11, bold=True,
                                color=SAGE if dark else GREEN)
        bounds = (x, H - top - height, x + width, H - top)
        if internal:
            self.pdf.linkRect('', url, bounds, thickness=0)
        else:
            self.pdf.linkURL(url, bounds, relative=0, thickness=0)
        return height

    def image(self, source, top, width=CONTENT):
        from PIL import Image
        with Image.open(source) as image:
            height = width * image.height / image.width
        self.pdf.drawImage(str(source), M, H - top - height, width=width, height=height, mask='auto')
        return height

    def item(self, title, detail, *, gap=14):
        title_height = self.paragraph(title, 0, size=13, bold=True, draw=False)
        body_height = self.paragraph(detail, 0, size=10.5, leading=16, draw=False)
        if self.y + title_height + body_height + 10 > H - 68:
            return False
        self.text(title, size=13, bold=True, color=FOREST, gap=4)
        self.text(detail, size=10.5, leading=16, gap=gap)
        return True


def cover(guide):
    guide.start('SOTOLAB  /  브랜드 소개서', dark=True)
    logo = ROOT / 'brand-kit/assets/logo-light.png'
    guide.pdf.drawImage(str(logo), W - M - 110, H - 56, width=110, height=36.75)
    guide.text('현장에서 쓸 도구를,\n수업에서 직접 만듭니다', size=40, leading=53,
               bold=True, color=PAPER, gap=27)
    guide.text('장성균 공학박사 · SotoLAB 프로젝트 교육', size=14, color=SAGE, gap=32)
    guide.y += guide.image(PHOTO, guide.y) + 13
    guide.text('IoTPlacement 3D 설계 화면 · AIoT 스마트 공간 실습에 활용', size=9.5, color=SAGE)
    guide.y += 24
    guide.text('기업 · 대학 · 기관 맞춤 교육 및 멘토링', size=13, color=PAPER)


def contents(guide):
    guide.start('SOTOLAB  /  목차')
    guide.text('프로젝트 교육 안내', size=33, bold=True, color=FOREST, gap=22)
    guide.text('교육 방식부터 연구·서비스·교육 이력과 멘티의 기록까지. 항목을 누르면 해당 장으로 이동합니다.',
               color=MUTED, width=380, gap=35)
    for number, (key, label) in enumerate([
        ('brand', 'SotoLAB이 수업을 만드는 방식'), ('class', '수업의 한 장면'),
        ('programs', '대상과 목표에 맞는 교육'), ('field', '개발 현장에서 수업까지'),
        ('letter', '오늘은 여기까지 왔네'), ('voices', '멘티가 직접 쓴 이야기'),
        ('research', '연구개발 · 특허와 발명'), ('product', '서비스 개발'),
        ('education', '교육·강연과 멘토링 이력'), ('career', '교육자 경력 · 썬스타 연혁'),
        ('books', '교재와 저서'), ('course-details', '교육 과정별 상세 안내'),
        ('testimonials', '멘티 소감 원문 14편'),
        ('contact', '교육 상담')
    ], 1):
        guide.rule(guide.y - 5)
        guide.paragraph(f'{number:02}', guide.y, size=10, color=MUTED, width=32)
        guide.link(label, guide.y, key, x=M + 40, width=CONTENT - 40, internal=True)
        guide.y += 34


def story(guide, reviews):
    guide.chapter('brand', '브랜드 소개', '직접 해온 경험을,\n함께 해내는 배움으로')
    guide.text('SotoLAB은 썬스타가 운영하는 교육·멘토링 브랜드입니다. 장성균 공학박사는 임베디드 시스템과 스마트폰 OS 개발로 시작해 IoT, 보안, 블록체인, AI로 연구와 개발을 넓혀 왔습니다. 지금은 현장에서 기술을 연결하고 검증해 온 경험을 강연과 프로젝트 수업으로 옮깁니다.', size=13, gap=26)
    guide.text('배워서 남주자', size=25, bold=True, color=GREEN, gap=8)
    guide.text('배우는 사람이 자신의 경험을 동료와 나누고, 다음 사람의 멘토가 되는 수업을 지향합니다. 소프트웨어 윤리와 친절한 마음을 바탕으로 사람들의 삶에 도움이 되는 기술을 함께 만들어 가려 합니다. 이를 소토피아(Sotopia)라 부릅니다.', size=13, gap=25)
    guide.rule(guide.y)
    guide.y += 22
    guide.text('좋은 개발 습관이 좋은 개발팀을 만듭니다', size=17, bold=True, color=FOREST, gap=9)
    guide.text('기업 멘토링에서는 구성원이 자신의 업무 문제를 가져옵니다. 작은 과제를 직접 실행하고 서로의 결과를 검토하며, 다시 쓸 수 있는 도구와 작업 방법을 팀에 남깁니다.', width=435)

    guide.chapter('class', '프로젝트 실습', '반복 업무 하나를\n직접 쓰는 도구로', '실습 예시  /  주간 보고서 초안 도구')
    guide.text('한 팀이 매주 여러 문서에서 진행 상황을 모아 같은 양식으로 정리합니다. 수업에서는 그 과정에서 시간이 가장 많이 드는 일을 하나 고릅니다. 어떤 자료를 받아 어떤 결과를 만들면 도움이 될지 정하고, 팀이 직접 써볼 수 있는 첫 화면을 구현합니다.', size=13, gap=26)
    for number, title, body in [
        ('01', '문제와 입력을 정합니다', '정리할 항목과 입력 파일, 결과물에 포함할 내용을 고릅니다.'),
        ('02', '핵심 기능을 구현합니다', '샘플 파일에서 정보를 뽑아 정해진 형식의 초안을 만드는 흐름을 구성합니다.'),
        ('03', '샘플로 결과를 검증합니다', '누락된 항목과 예상 밖 입력을 확인하고, 사람이 검토할 기준을 정합니다.'),
        ('04', '다음 사람이 쓸 수 있게 정리합니다', '사용 절차와 남은 개선점을 기록해 팀이 이어서 적용할 수 있게 합니다.'),
    ]:
        guide.rule(guide.y)
        guide.y += 12
        guide.text(f'{number}   {title}', size=15, bold=True, color=GREEN, gap=3)
        guide.text(body, size=11, gap=16)
    guide.text('교육 시간과 수준에 따라 문제 정의서, 기초 실습 결과, 검증 가능한 프로토타입까지 범위를 정합니다.', size=11, color=MUTED)

    guide.chapter('programs', '교육 과정', '대상과 목표에 맞는 교육', '기업, 대학, 기관이 해결하고 싶은 과제에서 출발합니다.')
    for title, description in [
        ('기업 · AI 업무 도구와 멘토링', 'AI 업무 활용 기본 교육, 실무자 집중 워크숍, 업무 도구 제작 세션, 도입 전략 브리핑을 제공합니다. 실제 업무를 기준으로 핵심 실무자부터 시작해 팀에 적용하는 방식을 함께 설계합니다.'),
        ('대학 · AIoT 스마트 공간과 캡스톤', '공간 시나리오, 장치 배치, 센서·조명 자동화를 다룹니다. 키트와 IoTPlacement를 활용해 설계를 검증하고, 캡스톤에서는 아이디어를 설계와 구현으로 구체화합니다.'),
        ('기관 · 기술 특강과 프로젝트 실습', '임베디드와 IoT 플랫폼, 블록체인 구조와 서비스, 보안 설계의 핵심을 대상으로 맞춥니다. 강연, 집중 실습, 프로젝트 멘토링으로 진행 범위를 조정합니다.'),
    ]:
        assert guide.item(title, description)
    guide.y += 8
    guide.y += guide.image(PLAN, guide.y, width=360) + 8
    guide.text('IoTPlacement 평면 배치 화면 · 기기 배치와 설계 검토에 사용', size=9, color=MUTED)

    guide.chapter('field', '실제 사례', '개발 현장에서 수업까지',
                  '서비스에서 선택한 기술과 연결 방법을, 수업에서 검증할 수 있는 과제로 바꿉니다.')
    for title, body in [
        ('에코브리티 · AI 무인 회수 로봇과 웹 운영 화면',
         '회수 로봇과 연계한 웹 기반 통합 관리 시스템의 개발과 서비스 관리를 총괄했습니다. 수업에서는 장치에서 생긴 데이터가 서버를 거쳐 운영 화면에 표시되는 흐름을 설계해 봅니다.'),
        ('블록체인 응용 서비스 · 서비스 흐름과 스마트 계약',
         '출입·예약과 제주감귤나무 등 응용 사례 및 스마트 계약 플랫폼 통합 모듈을 개발했습니다. 이 경험으로 어떤 거래에 스마트 계약이 필요한지 판단하는 설계 과정을 설명합니다.'),
        ('NFC 보안 인증 · 로컬 기술 검증',
         '실물 카드, 인증 서버, 웹 화면을 연결한 개념검증 사례입니다. 실습에서는 기기 인증과 서비스 접근 권한을 각각 어떻게 확인하는지 다룹니다.'),
        ('가톨릭대학교 · AIoT 스마트홈 인테리어 특강',
         '관련 전공 학생들이 공간 시나리오를 설계하고 실제 기기를 연결해 자동화를 실습했습니다. 대학 공식 뉴스룸에서 당시 교육 현장을 확인할 수 있습니다.'),
    ]:
        assert guide.item(title, body)
        if title.startswith('에코브리티'):
            node_width = (CONTENT - 36) / 3
            for index, label in enumerate(['회수 로봇', '서버 · 데이터', '웹 운영 화면']):
                x = M + index * (node_width + 18)
                guide.box(x, guide.y, node_width, 35, TINT)
                guide.paragraph(label, guide.y + 9, x=x + 10, width=node_width - 20,
                                size=10, bold=True, color=GREEN)
                if index < 2:
                    guide.paragraph('→', guide.y + 8, x=x + node_width + 3, width=15,
                                    size=10, color=GREEN)
            guide.y += 55
    guide.y += 6
    guide.link('가톨릭대학교 공식 교육 현장 기사 보기', guide.y, UNIVERSITY)

    guide.chapter('letter', '멘토의 작은 이야기', '오늘은 여기까지 왔네')
    letter = tree('data/mentoring-content.html').xpath('//*[@id="mentor-story"]//p[not(@class="s-eyebrow")]')
    for paragraph in letter:
        value = plain(paragraph)
        closing = 's-mentor-letter-closing' in (paragraph.get('class') or '')
        guide.text(value, size=13, leading=23, gap=22, bold=closing,
                   color=GREEN if closing else INK, width=465)

    guide.chapter('voices', '멘티의 목소리', '멘티가 직접 쓴 이야기',
                  '개발자로의 전환, 졸업작품, 첫 실무에서 멘티들이 마주한 질문입니다.')
    for label, description, quote in [
        ('QA 엔지니어 · 개발자로의 전환',
         '파이썬 독학을 이어가기 어려웠던 QA 엔지니어가, 공부한 내용을 직접 설명하며 이해한 부분과 막힌 부분을 구체적으로 확인한 이야기입니다.',
         '제 자신이 먼저 이해를 하고 있는지를 확인하면서 공부를 하는 습관을 기를 수 있었습니다.'),
        ('대학생 · AI 졸업작품',
         '기업에서 의뢰한 과제를 졸업작품으로 만들던 학생이, 모바일 앱·백엔드·AI가 어떻게 맞물리는지 프로젝트의 방향을 잡아가는 이야기입니다.',
         '캡스톤 프로젝트를 위한 프로그래밍 지식과 더불어 CS 지식을 함께 공부하면서 더 깊게 학습할 수 있는 것이 정말 좋다고 생각합니다.'),
        ('IT 인턴 · 첫 실무',
         '첫 출근 날 받은 조사 과제를 설명하고 피드백을 받으면서, 낯선 지식을 스스로 정리하는 법을 익힌 인턴의 이야기입니다.',
         '이전에는 할 수 있는 업무가 없는 나라고 생각했었지만 마지막에는 주어진 업무도 해내는 나를 볼 수 있었다.'),
    ]:
        guide.rule(guide.y)
        guide.y += 13
        guide.text(label, size=15, bold=True, color=GREEN, gap=6)
        guide.text(description, size=11, gap=6)
        assert any(quote in body for _, body in reviews), quote
        guide.text('“' + quote + '”', size=11, width=440, color=FOREST, gap=20)
    guide.link('멘티 소감 원문 14편 읽기', guide.y, 'testimonials', internal=True)


def archive(guide, rows):
    sections = [
        ('research', '연구개발 · 특허와 발명', ('research', 'patent')),
        ('product', '서비스 개발', ('product',)),
        ('education', '교육·강연과 멘토링 이력', ('education', 'mentoring')),
    ]
    for key, title, categories in sections:
        guide.chapter(key, '활동 기록', title)
        for category in categories:
            selected = sorted((row for row in rows if row['category'] == category),
                              key=lambda row: (re.search(r'\d{4}', row['period']) or ['9999'])[0])
            for row in selected:
                guide_entry(guide, title, row['title'],
                            f"{row['period']}   /   {row['organization']}\n{row['role']}\n{row['result']}\n수업 연결  ·  {row['lesson']}",
                            row.get('public_url'), row.get('link_label', '공개 자료 보기'))


def guide_entry(guide, section, title, body, url=None, link_label='자세히 보기'):
    title_height = guide.paragraph(title, 0, size=13, bold=True, draw=False)
    body_height = guide.paragraph(body, 0, size=10.5, leading=16, draw=False)
    if guide.y + title_height + body_height + (43 if url else 21) > H - 65:
        guide.start('활동 기록  /  ' + section)
    guide.rule(guide.y - 5)
    assert guide.item(title, body, gap=10 if url else 21)
    if url:
        guide.y += guide.link(link_label, guide.y - 6, url) + 13


def reference(guide):
    guide.chapter('career', '교육자 소개', '교육자 경력 · 썬스타 연혁',
                  '장성균 공학박사의 개인 경력과 썬스타·SotoLAB 활동 기록을 담았습니다.')
    profile = tree('profile.html')
    for item in profile.xpath('//*[@id="career"]//ol/li'):
        guide_entry(guide, '교육자 경력', plain(item.xpath('./strong')[0]), plain(item.xpath('./span')[0]))
    for item in tree('history.html').xpath('//*[@id="history"]//li[h2 or div/h2]'):
        heading = item.xpath('.//h2')[0]
        guide_entry(guide, '썬스타 연혁', plain(heading),
                    '\n'.join(plain(node) for node in item.xpath('./span | .//p')))
    for item in tree('history.html').xpath('//main//section[not(@id)]//li'):
        guide_entry(guide, '썬스타 연혁', plain(item), '썬스타 설립 이전 활동')
    guide.start('교육자 경력  /  출강 이력')
    guide.text('기관과 대상별 강의 이력', size=25, bold=True, color=FOREST, gap=20)
    for row in profile.xpath('//*[@id="teaching"]//tbody/tr'):
        period, organization, subject = [plain(cell) for cell in row.xpath('./td')]
        guide_entry(guide, '기관과 대상별 강의 이력', organization, f'{period}   /   {subject}')

    guide.chapter('books', '수업 자료', '교재와 저서')
    source = tree('books.html')
    for book in source.xpath('//*[@id="publications"]//article'):
        title = plain(book.xpath('.//h2')[0])
        detail = '\n'.join(plain(node) for node in book.xpath('.//p'))
        link = book.xpath('.//a[starts-with(@href, "https://")][1]/@href')
        guide_entry(guide, '교재와 저서', title, detail, link[0] if link else None)
    for article in source.xpath('//*[@id="learning-materials"]//*[self::article or self::div][./h3]'):
        guide_entry(guide, '실습 자료', plain(article.xpath('./h3')[0]),
                    '\n'.join(plain(node) for node in article.xpath('./p')))
    guide.chapter('course-details', '교육 과정  /  상세 안내', 'AIoT 실습 과정과 맞춤 특강',
                  '시간과 운영 조건은 상담할 때 확인하실 수 있습니다.')
    academy = tree('data/academy-content.html')
    for entry in academy.xpath('//*[@id="custom-lectures"]//article | //*[@id="courses"]//a[.//h3]'):
        heading = entry.xpath('.//h3')
        detail = '\n'.join(plain(node) for node in entry.xpath(
            './/p | .//h4 | .//div[@class="s-course-meta"]/span'))
        guide_entry(guide, 'AIoT 실습 과정과 맞춤 특강', plain(heading[0]), detail)
    guide.start('교육 과정  /  기업 교육')
    guide.text('기업 교육과 팀 적용', size=25, bold=True, color=FOREST, gap=18)
    enterprise = tree('online.html')
    for card in enterprise.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," course-card ")]'):
        title = card.xpath('.//h2')
        if title:
            detail = '\n'.join(plain(node) for node in card.xpath('.//p | .//li'))
            guide_entry(guide, '기업 교육', plain(title[0]), detail)
    for node in tree('curriculum.html').xpath('//*[contains(concat(" ",normalize-space(@class)," ")," sote-step ")]'):
        title = node.xpath('.//h3')
        if title:
            detail = '\n'.join(plain(child) for child in node.xpath('.//p | .//li'))
            guide_entry(guide, '기업 교육', plain(title[0]), detail)
    guide.start('교육 과정  /  실습 과제')
    guide.text('업무 도구 실습 예시', size=25, bold=True, color=FOREST, gap=16)
    guide.text('반복 업무에서 개선할 부분을 고를 때 살펴볼 수 있는 과제입니다.',
               color=MUTED, gap=24)
    for card in tree('mvp-projects.html').xpath('//*[contains(concat(" ",normalize-space(@class)," ")," project-card ")]'):
        title = card.xpath('.//h3')
        if title:
            detail = '\n'.join(plain(node) for node in card.xpath('.//p'))
            guide_entry(guide, '업무 도구 실습 예시', plain(title[0]), detail)


def original_reviews(guide, reviews):
    for index, (name, body) in enumerate(reviews, 1):
        guide.start(f'멘티 소감 원문  /  {index:02} / {len(reviews)}')
        if index == 1:
            guide.pdf.bookmarkPage('testimonials')
            guide.pdf.addOutlineEntry('멘티 소감 원문 14편', 'testimonials', level=0)
        guide.text(name, size=24, bold=True, color=FOREST, gap=13)
        guide.rule(guide.y)
        guide.y += 15
        if index == 1:
            guide.text('이전 SotoLAB 사이트에 공개된 「멘토티멘토링 후기」입니다. 작성자 익명 표기를 그대로 담았습니다.',
                       size=10, color=MUTED, gap=14)
        size, leading = 11, 17
        if guide.paragraph(body, 0, size=size, leading=leading, draw=False) + guide.y > H - 57:
            size, leading = 10.5, 15.6
        guide.text(body, size=size, leading=leading)


def contact(guide):
    guide.start('교육 상담', dark=True)
    guide.pdf.bookmarkPage('contact')
    guide.pdf.addOutlineEntry('교육 상담', 'contact', level=0)
    guide.text('첫 실습 주제를\n함께 정해볼까요?', size=37, leading=50, bold=True, color=PAPER, gap=24)
    guide.text('반복해서 하는 업무나 학생들과 만들어 보고 싶은 아이디어를 알려주세요. 첫 수업에서 어디까지 만들어 볼 수 있을지 함께 정합니다.', size=14, color=PAPER, width=400, gap=26)
    guide.text('교육 대상   /   해보고 싶은 과제   /   희망 시기', size=12, bold=True, color=SAGE, gap=35)
    for label, url in [
        ('SotoLAB 교육 문의 페이지', INQUIRY),
        ('카카오톡 문의', 'https://open.kakao.com/o/sK8hYXfb'),
        ('이메일  sotolabedu@gmail.com', 'mailto:sotolabedu@gmail.com'),
    ]:
        guide.y += guide.link(label, guide.y, url, dark=True, width=310) + 12
    guide.y += 18
    size = 116
    code = QrCodeWidget(INQUIRY)
    x0, y0, x1, y1 = code.getBounds()
    drawing = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
    drawing.add(code)
    guide.box(M, guide.y, size, size, white)
    renderPDF.draw(drawing, guide.pdf, M, H - guide.y - size)
    guide.pdf.linkURL(INQUIRY, (M, H - guide.y - size, M + size, H - guide.y), thickness=0)
    guide.y += size + 12
    guide.text('QR로 교육 문의 열기', size=10, color=SAGE)


def main():
    guide = Guide()
    reviews = excerpts()
    rows = json.loads((ROOT / 'data/experience.json').read_text(encoding='utf-8-sig'))
    cover(guide)
    contents(guide)
    story(guide, reviews)
    archive(guide, rows)
    reference(guide)
    original_reviews(guide, reviews)
    contact(guide)
    guide.pdf.save()
    print(f'{guide.page} pages, {len(rows)} activity records, {len(reviews)} original testimonials')


if __name__ == '__main__':
    main()

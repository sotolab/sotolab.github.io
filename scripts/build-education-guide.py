"""Build the public SotoLAB education PDF from the site's published records."""
import json
import os
from pathlib import Path
import re
import subprocess
from xml.sax.saxutils import escape

from lxml import html
from PIL import Image
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
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
FOREST = HexColor('#20392b')
GREEN = HexColor('#3a5745')
SAGE = HexColor('#d5dfcb')
INK = HexColor('#212d24')
MUTED = HexColor('#536052')
PAPER = HexColor('#f4efe4')
LINE = HexColor('#c9c8b8')
CLAY = HexColor('#9e442c')
WARM = HexColor('#e9b490')
WORKBENCH = ROOT / 'img/sotolab-workbench.webp'
DESK = ROOT / 'img/sotolab-notebook.webp'
PHOTO = ROOT / 'img/academy-simulator-3d.png'

for name, filename in [('KR', 'malgun.ttf'), ('KR-Bold', 'malgunbd.ttf'),
                       ('Display', 'HANBatangB.ttf'), ('Serif', 'HANBatang.ttf')]:
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
        self.pdf.setTitle('SotoLAB · 수업이 끝나면, 무엇이 남나요?')
        self.pdf.setAuthor('SotoLAB · Sunstar')
        self.page = 0
        self.y = 0
        self.word_wrap = None

    def box(self, x, top, width, height, color):
        self.pdf.setFillColor(color)
        self.pdf.rect(x, H - top - height, width, height, fill=1, stroke=0)

    def rule(self, top, color=LINE):
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(.7)
        self.pdf.line(M, H - top, W - M, H - top)

    def paragraph(self, value, top, *, x=M, width=CONTENT, size=12, leading=None, bold=False, font=None,
                  color=INK, draw=True):
        style = ParagraphStyle(
            'guide', fontName=font or ('KR-Bold' if bold else 'KR'), fontSize=size,
            leading=leading or size * 1.62, textColor=color, alignment=TA_LEFT,
            wordWrap=self.word_wrap)
        rendered = Paragraph(escape(value).replace('\n', '<br/>'), style)
        _, height = rendered.wrap(width, H)
        if draw:
            if top + height > H - 49:
                raise ValueError(f'Page {self.page} overflow at {top + height:.1f}: {value[:45]}')
            rendered.drawOn(self.pdf, x, H - top - height)
        return height

    def text(self, value, *, size=12, leading=None, gap=14, color=INK, bold=False,
             font=None, width=CONTENT):
        self.y += self.paragraph(value, self.y, width=width, size=size,
                                 leading=leading, color=color, bold=bold, font=font) + gap

    def start(self, label=None, *, dark=False):
        if self.page:
            self.pdf.showPage()
        self.page += 1
        self.box(0, 0, W, H, FOREST if dark else PAPER)
        self.y = 90
        self.word_wrap = 'CJK' if label else None
        if label is None:
            return
        accent = SAGE if dark else GREEN
        self.paragraph(label, 39, size=10, bold=True, color=accent)
        self.rule(61, HexColor('#597660') if dark else LINE)
        self.rule(H - 46, HexColor('#597660') if dark else LINE)
        self.pdf.setFont('KR', 8)
        self.pdf.setFillColor(accent)
        self.pdf.drawString(M, 28, 'SotoLAB  /  프로젝트 교육 안내')
        self.pdf.drawRightString(W - M, 28, str(self.page).zfill(2))

    def mark(self, key, title):
        self.pdf.bookmarkPage(key)
        self.pdf.addOutlineEntry(title, key, level=0)

    def chapter(self, key, label, title, intro=None):
        self.start(label)
        self.mark(key, title)
        self.text(title, size=29, leading=39, font='Display', gap=17, color=FOREST)
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

    def photograph(self, source, x, top, width, height, *, focus=.5):
        with Image.open(source) as image:
            scale = max(width / image.width, height / image.height)
            draw_width, draw_height = image.width * scale, image.height * scale
            self.pdf.saveState()
            clip = self.pdf.beginPath()
            clip.rect(x, H - top - height, width, height)
            self.pdf.clipPath(clip, stroke=0, fill=0)
            self.pdf.drawImage(ImageReader(image), x - (draw_width - width) * focus,
                               H - top - height - (draw_height - height) / 2,
                               width=draw_width, height=draw_height)
            self.pdf.restoreState()

    def item(self, title, detail, *, gap=14):
        title_height = self.paragraph(title, 0, size=13, bold=True, draw=False)
        body_height = self.paragraph(detail, 0, size=10.5, leading=16, draw=False)
        if self.y + title_height + body_height + 10 > H - 68:
            return False
        self.text(title, size=13, bold=True, color=FOREST, gap=4)
        self.text(detail, size=10.5, leading=16, gap=gap)
        return True


def cover(guide):
    guide.start()
    guide.photograph(WORKBENCH, 0, 315, W, 445, focus=.62)
    guide.box(0, 760, W, H - 760, FOREST)
    logo = ROOT / 'brand-kit/assets/logo-light.png'
    guide.pdf.drawImage(str(logo), M - 6, H - 71, width=113, height=37.75,
                        mask=[244, 255, 244, 255, 244, 255])
    guide.paragraph('프로젝트 교육 · 브랜드 브로셔', 47, x=353, width=190,
                    size=10, color=MUTED)
    guide.rule(91)
    guide.paragraph('수업이 끝나면,\n무엇이 남나요?', 111, size=53, leading=67,
                    font='Display', color=FOREST)
    guide.paragraph('자기 현장의 과제를 가져와 첫 결과물을 만드는 수업', 264,
                    size=13, color=MUTED)
    guide.paragraph('장성균 공학박사 · SotoLAB', 774, size=10, bold=True, color=SAGE)
    guide.link('목차 및 상세 기록 보기', 774, 'contents', x=388, width=154,
               internal=True, dark=True)


def contents(guide):
    guide.start()
    guide.mark('contents', '목차와 상세 기록')
    guide.box(0, 0, W, 226, FOREST)
    guide.paragraph('SOTOLAB', 45, size=11, bold=True, color=WARM)
    guide.paragraph('목차와 상세 기록', 78, size=43, leading=54,
                    font='Display', color=PAPER)
    guide.paragraph('항목을 누르면 해당 페이지로 이동합니다.', 153,
                    size=12, color=SAGE)
    groups = [
        ('브랜드와 교육', [
            ('brand', '직접 만들어 온 경험을, 수업으로'), ('class', '반복 업무에서 출발하는 실습'),
            ('programs', '기업·대학·기관 교육'), ('field', '개발 현장에서 수업까지'),
            ('letter', '오늘은 여기까지 왔네'), ('voices', '멘티가 직접 쓴 이야기'),
            ('contact', '교육 상담')]),
        ('상세 자료', [
            ('research', '연구개발 · 특허와 발명'), ('product', '서비스 개발'),
            ('education', '교육·강연과 멘토링 이력'), ('career', '교육자 경력 · 썬스타 연혁'),
            ('books', '교재와 저서'), ('course-details', '교육 과정별 상세 안내'),
            ('testimonials', '멘티 소감 원문 14편')]),
    ]
    for column, (label, entries) in enumerate(groups):
        x = M + column * 255
        guide.paragraph(label, 265, x=x, width=230, size=20, font='Display', color=FOREST)
        for i, (key, title) in enumerate(entries):
            top = 315 + i * 46
            guide.box(x, top - 7, 231, .55, LINE)
            guide.link(title, top, key, x=x, width=231, internal=True)
    guide.rule(761)
    guide.paragraph('SotoLAB · 썬스타', 773, size=10, color=MUTED)


def opening(guide, key, label, title, *, dark=False):
    guide.start(dark=dark)
    guide.mark(key, title.replace('\n', ' '))
    guide.paragraph(label, 53, size=11, bold=True, color=WARM if dark else CLAY)
    guide.paragraph(title, 88, size=35, leading=48, font='Display',
                    color=PAPER if dark else FOREST)


def story(guide, reviews):
    opening(guide, 'brand', 'SotoLAB이 가르치는 방식', '직접 만들어 온 경험을,\n수업으로.')
    guide.photograph(DESK, 0, 235, 286, 553, focus=.47)
    guide.paragraph('개발에서 시작했습니다.', 261, x=320, width=219, size=19,
                    leading=28, font='Display', color=FOREST)
    guide.paragraph('장성균 공학박사는 임베디드 시스템과 스마트폰 OS를 개발하고, IoT·보안·블록체인·AI를 연구해 왔습니다. 장치와 데이터, 화면을 연결하고 현장에서 검증한 경험이 수업의 출발점입니다.',
                    309, x=320, width=219, size=12.5, leading=22, color=MUTED)
    guide.box(320, 485, 221, .7, LINE)
    guide.paragraph('배워서 남주자.', 516, x=320, width=219, size=28,
                    leading=38, font='Display', color=CLAY)
    guide.paragraph('배운 사람이 동료에게 경험을 나누고, 다음 사람의 멘토가 되기를 바랍니다. 소프트웨어 윤리와 친절을 바탕으로 삶에 도움이 되는 기술을 만드는 일. SotoLAB이 말하는 소토피아(Sotopia)입니다.',
                    573, x=320, width=219, size=12.5, leading=22)
    guide.paragraph('SotoLAB은 썬스타의 교육·멘토링 브랜드입니다.', 775, x=320,
                    width=221, size=9, color=MUTED)

    opening(guide, 'class', '실습 예시  /  주간 보고서 초안 도구', '매주 반복하는 일을\n작은 도구 하나로.')
    guide.paragraph('여러 문서에서 진행 상황을 모아 같은 양식에 옮기는 팀이 있습니다. 수업에서는 이 업무를 가져와, 당장 확인해 볼 수 있는 기능 하나부터 만듭니다.',
                    203, size=13, leading=22, width=420, color=MUTED)
    guide.box(M, 281, CONTENT, 178, FOREST)
    guide.paragraph('만들어 볼 결과물', 302, x=M + 22, width=420, size=10,
                    bold=True, color=WARM)
    guide.paragraph('주간 보고서 초안', 333, x=M + 22, width=430, size=31,
                    leading=39, font='Display', color=PAPER)
    guide.paragraph('샘플 자료에서 진행 현황·이슈·다음 할 일을 정리합니다.\n자료가 비어 있거나 내용이 애매하면 검토 항목으로 표시합니다.',
                    396, x=M + 22, width=440, size=11, leading=18, color=SAGE)
    for i, (title, body) in enumerate([
        ('고릅니다', '업무 흐름에서 먼저 줄일 일을 하나 정합니다.'),
        ('만듭니다', '샘플 입력에서 정해진 형식의 초안이 나오게 합니다.'),
        ('검증합니다', '누락과 예외를 확인하고 사람이 판단할 기준을 적습니다.'),
    ]):
        x = M + i * 168
        guide.box(x, 496, 153, .7, LINE)
        guide.paragraph(title, 516, x=x, width=153, size=18, font='Display', color=CLAY)
        guide.paragraph(body, 558, x=x, width=145, size=11, leading=18, color=MUTED)
    guide.paragraph('교육 시간에 맞춰 문제 정의서, 기초 실습, 검증 가능한 프로토타입 중 도달할 범위를 정합니다.',
                    691, size=11, color=MUTED, width=430)

    opening(guide, 'programs', '기업·대학·기관 맞춤 교육', '어떤 결과물을\n만들어 보고 싶으신가요?')
    guide.box(M, 213, CONTENT, 1, LINE)
    for i, (label, title, body) in enumerate([
        ('기업', '내 업무에 쓸 도구', '반복 업무 하나를 골라 AI로 자료를 정리하거나 초안을 만드는 도구를 구현합니다. 실무자 워크숍과 팀 멘토링으로 적용을 이어갑니다.'),
        ('대학·기관', '실제로 반응하는 공간', '센서와 조명을 연결하고 사람이 들어오면 조명이 켜지는 장면을 설계합니다. 키트 실습과 캡스톤, 기관 맞춤 특강으로 진행할 수 있습니다.'),
    ]):
        x = M + i * 253
        guide.paragraph(label, 230, x=x, width=231, size=10, bold=True, color=CLAY)
        guide.paragraph(title, 258, x=x, width=231, size=21, font='Display', color=FOREST)
        guide.paragraph(body, 305, x=x, width=223, size=11.5, leading=19, color=MUTED)
    guide.photograph(PHOTO, M, 409, CONTENT, 273)
    guide.paragraph('실제 실습 자료 · IoTPlacement 3D 공간 설계 화면', 699,
                    size=9.5, color=MUTED)
    guide.link('교육 과정별 상세 안내', 742, 'course-details', internal=True)

    opening(guide, 'field', '개발 경험이 수업이 되는 과정', '장치에서 화면까지,\n연결해 본 사람이 가르칩니다.', dark=True)
    guide.paragraph('에코브리티에서는 AI 무인 회수 로봇과 연동되는 웹 관리 시스템의 개발과 운영 관리를 총괄했습니다. 장치의 동작을 운영 화면과 연결한 경험을, 수업에서 데이터가 이동하는 흐름을 설계하는 과제로 가져옵니다.',
                    213, size=13, leading=23, color=SAGE, width=430)
    for i, (label, body) in enumerate([
        ('회수 로봇', '장치에서 신호를 받습니다.'),
        ('서버', '상태와 기록을 저장합니다.'),
        ('웹 화면', '운영자가 상태를 확인합니다.'),
    ]):
        x = M + i * 166
        guide.box(x, 344, 155, 97, HexColor('#2d4838'))
        guide.paragraph(label, 359, x=x + 12, width=135, size=16, font='Display', color=PAPER)
        guide.paragraph(body, 397, x=x + 12, width=132, size=9.5, color=SAGE)
    guide.paragraph('이 경험을 다른 주제에도 연결합니다.', 496, size=21,
                    font='Display', color=WARM)
    guide.paragraph('블록체인 응용 서비스에서는 거래 흐름과 스마트 계약의 쓰임을, NFC 인증 개념검증에서는 기기 인증과 서비스 접근 권한을 각각 다룹니다. 가톨릭대학교 AIoT 특강에서는 학생들이 공간 시나리오를 설계하고 실제 기기를 연결했습니다.',
                    547, size=12, leading=22, width=455, color=SAGE)
    guide.link('가톨릭대학교 공식 교육 현장 기사', 669, UNIVERSITY, dark=True)
    guide.link('연구개발과 서비스 이력 보기', 708, 'research', dark=True, internal=True)

    opening(guide, 'letter', '장성균의 편지', '오늘은 여기까지 왔네.')
    guide.box(M, 163, 34, 2, CLAY)
    guide.y = 191
    letter = tree('data/mentoring-content.html').xpath('//*[@id="mentor-story"]//p[not(@class="s-eyebrow")]')
    for paragraph in letter:
        closing = 's-mentor-letter-closing' in (paragraph.get('class') or '')
        guide.text(plain(paragraph), size=13.5, leading=24, gap=20,
                   font='Display' if closing else 'Serif', color=GREEN if closing else INK,
                   width=463)

    opening(guide, 'voices', '이전 멘토링에 참여한 사람들의 소감', '배운 뒤, 각자의\n현장으로 돌아갔습니다.')
    for index, (label, quote) in enumerate([
        ('개발자로의 전환을 준비한 QA 엔지니어', '제 자신이 먼저 이해를 하고 있는지를 확인하면서 공부를 하는 습관을 기를 수 있었습니다.'),
        ('AI 졸업작품을 진행한 대학생', '캡스톤 프로젝트를 위한 프로그래밍 지식과 더불어 CS 지식을 함께 공부하면서 더 깊게 학습할 수 있는 것이 정말 좋다고 생각합니다.'),
        ('첫 실무를 경험한 IT 인턴', '마지막에는 주어진 업무도 해내는 나를 볼 수 있었다.'),
    ]):
        assert any(quote in body for _, body in reviews), quote
        top = 229 + index * 153
        guide.box(M, top - 9, CONTENT, .7, LINE)
        height = guide.paragraph('“' + quote + '”', top + 9, size=20, leading=29,
                                 font='Serif', color=FOREST, width=463)
        guide.paragraph(label, top + 21 + height, size=10, bold=True, color=CLAY)
    guide.link('멘티가 직접 쓴 소감 14편 읽기', 732, 'testimonials', internal=True)



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
    opening(guide, 'contact', 'SotoLAB 교육 상담', '함께 풀어볼\n과제 하나를 알려주세요.', dark=True)
    guide.paragraph('누가 참여하는지, 무엇을 만들어 보고 싶은지 알려주세요. 교육 시간과 참여자의 경험에 맞춰 첫 실습에서 어디까지 만들어 볼지 함께 정합니다.',
                    216, size=13, leading=23, width=425, color=SAGE)
    guide.box(M, 320, CONTENT, .7, HexColor('#758977'))
    guide.paragraph('교육 대상   /   해보고 싶은 과제   /   희망 시기',
                    347, size=11, bold=True, color=WARM)
    guide.y = 408
    for label, url in [
        ('SotoLAB 교육 문의 페이지', INQUIRY),
        ('카카오톡 문의', 'https://open.kakao.com/o/sK8hYXfb'),
        ('이메일  sotolabedu@gmail.com', 'mailto:sotolabedu@gmail.com'),
    ]:
        guide.y += guide.link(label, guide.y, url, dark=True, width=320) + 20
    size = 116
    qr_x, qr_y = W - M - size, 407
    code = QrCodeWidget(INQUIRY)
    x0, y0, x1, y1 = code.getBounds()
    drawing = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
    drawing.add(code)
    guide.box(qr_x, qr_y, size, size, white)
    renderPDF.draw(drawing, guide.pdf, qr_x, H - qr_y - size)
    guide.pdf.linkURL(INQUIRY, (qr_x, H - qr_y - size, qr_x + size, H - qr_y), thickness=0)
    guide.paragraph('QR로 교육 문의 열기', qr_y + size + 11, x=qr_x, width=size,
                    size=9, color=SAGE)
    guide.box(M, 651, CONTENT, .7, HexColor('#758977'))
    guide.link('상세 이력과 멘티 소감 원문 보기', 682, 'contents', dark=True, internal=True)
    guide.paragraph('표지와 작업대 이미지는 교육의 맥락을 표현한 연출 이미지입니다.',
                    755, size=9, color=SAGE)


def main():
    guide = Guide()
    reviews = excerpts()
    rows = json.loads((ROOT / 'data/experience.json').read_text(encoding='utf-8-sig'))
    cover(guide)
    story(guide, reviews)
    contact(guide)
    contents(guide)
    archive(guide, rows)
    reference(guide)
    original_reviews(guide, reviews)
    guide.pdf.save()
    print(f'{guide.page} pages, {len(rows)} activity records, {len(reviews)} original testimonials')


if __name__ == '__main__':
    main()

"""Build the public SotoLAB education PDF from the site's published records."""
import json
import os
from pathlib import Path
from io import BytesIO
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
AI_TRAINING = 'https://moel.go.kr/news/enews/report/enewsView.do?news_seq=18833'
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
SENSOR = ROOT / 'img/sotolab-sensor-study.webp'
PAVILION = ROOT / 'img/sotolab-space-study.webp'
AI_DESK = ROOT / 'img/sotolab-ai-workflow.webp'
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
        self.pdf.setTitle('SotoLAB · 기술의 깊이에서, 현장의 수업으로')
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
            compressed = BytesIO()
            image.convert('RGB').save(compressed, 'JPEG', quality=92, optimize=True)
            compressed.seek(0)
            self.pdf.drawImage(ImageReader(compressed), x - (draw_width - width) * focus,
                               H - top - height - (draw_height - height) / 2,
                               width=draw_width, height=draw_height)
            self.pdf.restoreState()


def cover(guide):
    guide.start(dark=True)
    guide.photograph(AI_DESK, 0, 302, W, 437, focus=.54)
    guide.box(0, 739, W, H - 739, FOREST)
    logo = ROOT / 'brand-kit/assets/logo-dark.png'
    guide.pdf.drawImage(str(logo), M - 8, H - 81, width=118, height=39.4,
                        mask=[0, 18, 0, 18, 0, 18])
    guide.paragraph('AI 응용 · 맞춤 실습교육', M + 8, x=387, width=154, size=11, color=SAGE)
    guide.rule(98, HexColor('#6d8570'))
    guide.paragraph('기술의 깊이에서,\n현장의 수업으로', 123, size=47, leading=59,
                    font='Display', color=PAPER)
    guide.paragraph('직접 해온 경험을, 함께 해내는 배움으로', 260,
                    size=13, color=WARM)
    guide.paragraph('장성균 공학박사 · 썬스타', 772, size=10, bold=True, color=SAGE)
    guide.link('목차와 상세 이력', 771, 'contents', x=395, width=146, internal=True, dark=True)


def contents(guide):
    guide.start()
    guide.mark('contents', '목차와 상세 이력')
    guide.box(0, 0, W, 216, FOREST)
    guide.paragraph('SotoLAB', 46, size=12, bold=True, color=WARM)
    guide.paragraph('목차와 상세 이력', 83, size=43, leading=54, font='Display', color=PAPER)
    guide.paragraph('항목을 누르면 해당 장으로 이동합니다.', 154, size=12, color=SAGE)
    groups = [
        ('브랜드와 교육', [
            ('brand', '직접 해온 경험을, 함께 해내는 배움으로'),
            ('history', '개발 현장에서 교육까지'),
            ('why', '왜 업무에 맞춘 AI 실습이 필요한가'),
            ('experience', '왜 SotoLAB이 설계할 수 있는가'),
            ('depth', 'AI 응용 교육의 세 가지 실습'),
            ('architecture', '사내 규정을 찾아 답하는 AI 서비스'),
            ('evaluation', 'AI 결과를 검증하고 운영하는 법'),
            ('technology', '블록체인 · 모바일 앱 · IoT · 정보보안'),
            ('operate', '스마트 공간으로 보는 기술 융합'),
            ('letter', '오늘은 여기까지 왔네')]),
        ('멘티 이야기와 상세 자료', [
            ('testimonials', '멘토링 소감문 다섯 편'),
            ('contact', '교육 상담'),
            ('research', '연구개발 · 특허와 발명'),
            ('product', '서비스 개발과 운영'),
            ('education', '교육·강연과 멘토링 이력'),
            ('career', '교육자 경력 · 썬스타 연혁'),
            ('books', '교재와 저서'),
            ('course-details', '교육 과정별 상세 안내')]),
    ]
    for column, (label, entries) in enumerate(groups):
        x = M + column * 255
        guide.paragraph(label, 259, x=x, width=231, size=19, font='Display', color=FOREST)
        for i, (key, title) in enumerate(entries):
            top = 306 + i * 39
            guide.box(x, top - 7, 231, .55, LINE)
            guide.link(title, top, key, x=x, width=231, internal=True)
    guide.rule(754)
    guide.paragraph('SotoLAB · 썬스타', 771, size=10, color=MUTED)


def opening(guide, key, label, title, *, dark=False):
    guide.start(dark=dark)
    guide.mark(key, title.replace('\n', ' '))
    guide.paragraph(label, 53, size=11, bold=True, color=WARM if dark else CLAY)
    guide.paragraph(title, 88, size=35, leading=47, font='Display',
                    color=PAPER if dark else FOREST)


def story(guide):
    opening(guide, 'brand', '브랜드 이야기', '직접 해온 경험을,\n함께 해내는 배움으로')
    guide.photograph(WORKBENCH, 0, 227, W, 295, focus=.56)
    guide.paragraph('기술이 낯선 사람에게,\n첫 결과물이 생기는 순간', 560, size=25, leading=36,
                    font='Display', width=260, color=FOREST)
    guide.paragraph('SotoLAB은 썬스타의 교육·멘토링 브랜드입니다. 개발자였던 장성균이 학생들의 첫 프로젝트를 함께하며 쌓아온 경험에서 시작했습니다. 배운 것을 자기 일에 써보고, 그 방법을 다음 사람에게 나눌 수 있는 수업을 만듭니다.',
                    566, x=322, width=219, size=11.5, leading=19, color=MUTED)
    guide.rule(729)
    guide.paragraph('교육철학  /  배워서 남주자', 750, size=11, bold=True, color=CLAY)
    guide.paragraph('소토피아(Sotopia)  /  삶에 도움이 되는 기술', 751, x=322,
                    width=219, size=9, color=MUTED)

    opening(guide, 'history', '장성균과 SotoLAB의 연혁', '만들고, 가르치고,\n다시 만들어 온 시간')
    for i, (year, title, body) in enumerate([
        ('2002', '장치에서 시작한 개발', '한컴MDS에서 임베디드 시스템 개발과 스마트폰 OS 포팅을 맡았습니다.'),
        ('2009–2010', '첫 프로젝트를 함께한 시간', '대학생의 위치기반 서비스, 안드로이드·웹 서비스, 근전도 기기 제어 프로젝트를 멘토링했습니다.'),
        ('2013–2015', '개발 경험을 수업으로', '한컴아카데미에서 과정 개발과 강의를 시작했습니다. 2015년부터 한양대 공학대학원에서 가르치고 썬스타·SotoLAB 활동을 시작했습니다.'),
        ('2015–2017', '제약이 큰 환경의 연구', '한국전자통신연구원 달 탐사 통신 과제에서 지상노드 소프트웨어 포팅에 참여했습니다.'),
        ('2018–2022', '서비스와 책으로 이어진 멘토링', '멘토티 웹·앱 서비스를 기획·개발하고, 멘토와 멘티의 경험을 『멘토티 멘토링』에 담았습니다.'),
        ('2026', '수업에 쓰는 도구도 직접 개발', 'IoTPlacement를 개발했습니다. 가톨릭대학교 특강에서는 학생들이 실제 기기를 연결하고 공간 자동화를 실습했습니다.'),
    ]):
        top = 220 + i * 84
        guide.rule(top)
        guide.paragraph(year, top + 15, width=105, size=13, bold=True, color=CLAY)
        guide.paragraph(title, top + 11, x=165, width=376, size=14, font='Display', color=FOREST)
        guide.paragraph(body, top + 35, x=165, width=376, size=10.5, leading=16, color=MUTED)
    guide.link('교육자 경력과 썬스타 연혁', 745, 'career', internal=True)

    opening(guide, 'why', '맞춤형 AI 교육이 필요한 이유', 'AI를 쓰는 사람과 일이\n달라지면 수업도 달라집니다')
    guide.paragraph('기업 실무자는 매주 반복하는 일을 줄이고 싶고, 대학생은 앱에서 동작하는 기능을 구현해야 할 수 있습니다. 참여자의 경험, 사용할 수 있는 자료와 교육 시간을 확인해, 수업에서 직접 시험할 결과물을 정합니다.',
                    211, size=13, leading=22, width=465, color=MUTED)
    for i, (label, title, body, goal) in enumerate([
        ('기업 실무자', '보고서 초안을 만드는 AI 도구', '샘플 자료에서 반복해서 정리하는 항목을 고릅니다. AI가 작성할 부분과 실무자가 확인할 부분을 정하고, 초안을 비교해 봅니다.', '결과물  /  보고서 초안 도구와 검토 기준'),
        ('대학·기관 프로젝트', '문서에서 답을 찾는 AI 앱', '사용자의 질문과 참고 문서를 연결합니다. 답변에 출처를 표시하고, 문서에 답이 없는 질문은 어떻게 안내할지 정합니다.', '결과물  /  작동하는 AI 앱과 검증용 질문'),
    ]):
        x = M + i * 251
        guide.box(x, 319, 236, 253, HexColor('#e6e8d9'))
        guide.paragraph(label, 338, x=x + 17, width=201, size=10, bold=True, color=CLAY)
        guide.paragraph(title, 369, x=x + 17, width=201, size=19, leading=26, font='Display')
        guide.paragraph(body, 434, x=x + 17, width=201, size=11, leading=18, color=MUTED)
        guide.paragraph(goal, 529, x=x + 17, width=201, size=9, leading=14, bold=True, color=FOREST)
    guide.rule(617)
    guide.paragraph('과제 파악 → 실습 설계 → 구현 → 검증과 피드백', 640, size=17,
                    font='Display', color=FOREST)
    guide.paragraph('고용노동부는 2026년 AI 앱 개발과 융합 직무를 포함한 현업 프로젝트형 훈련을 추진했습니다.', 686,
                    size=11, color=MUTED)
    guide.link('고용노동부 2026년 AI 캠퍼스 운영 자료', 739, AI_TRAINING)

    opening(guide, 'experience', 'SotoLAB이 교육을 설계할 수 있는 이유', '실무에서 내린 판단이\n수업의 순서를 정합니다')
    for i, (title, body) in enumerate([
        ('AI 연구와 구현  /  모델을 사용자가 쓰는 기능으로',
         '머신러닝을 적용한 보안·네트워크 연구를 총괄하고 객체 인식 앱을 개발했습니다. 이 경험을 바탕으로 모델의 입력, 실패 조건, 결과를 보여주는 화면을 함께 설계합니다.'),
        ('현업 서비스 운영  /  기능보다 먼저 살피는 업무 흐름',
         '에코브리티에서는 회수 로봇과 웹 관리 시스템을 연결하는 개발과 서비스 관리를 총괄했습니다. 입찰비서를 개발·운영하면서는 공고 검색부터 검토와 마감 관리까지 실제 업무 흐름을 다뤘습니다.'),
        ('특허와 발명  /  동작 조건을 구체적으로 확인하는 습관',
         'BLE 무선 장치 제어 특허와 재활용 플라스틱 보상 장치 발명 참여 경험을 바탕으로, 장치가 어떤 입력을 받고 어떤 조건에서 동작하는지 구체적으로 다룹니다.'),
        ('멘토링과 집필  /  각자의 출발점에서 시작하는 설명',
         '대학생·청년의 프로젝트 멘토링과 『임베디드 스케치』, 『오늘부터 나도 블록체인 앱 메이커』, 『멘토티 멘토링』 집필 경험을 실습 순서와 피드백 방식에 반영합니다.'),
    ]):
        top = 226 + i * 121
        guide.rule(top)
        guide.paragraph(title, top + 12, size=15, leading=21, font='Display', color=FOREST)
        guide.paragraph(body, top + 44, size=11.2, leading=18, color=MUTED)
    guide.link('연구개발과 특허 이력', 732, 'research', width=231, internal=True)
    guide.link('서비스 개발과 운영 기록', 732, 'product', x=310, width=231, internal=True)

    opening(guide, 'depth', 'AI 응용 기술  /  맞춤 실습 커리큘럼', '업무에 쓰고,\n도구로 만들고,\n서비스로 연결합니다', dark=True)
    for i, (label, title, description, result) in enumerate([
        ('실무자', '생성형 AI로 반복 업무 개선',
         '회의 기록·보고서·문의 메일 중 반복이 많은 과제를 고릅니다. 출력 양식과 검토 기준을 만들어 사람이 확인할 부분을 정합니다.',
         '결과물  /  팀이 다시 쓰는 업무 절차와 초안 양식'),
        ('팀·기획자', '사내 자료를 찾아 답하는 도구',
         '규정과 업무 문서를 검색해 관련 내용을 찾고, 답변 옆에 근거를 붙입니다. 문서에 답이 없으면 담당자에게 문의하도록 설계합니다.',
         '결과물  /  출처가 표시되는 문서 질의응답 도구'),
        ('개발자·대학 프로젝트', 'AI 기능을 앱·웹에 연결',
         '모델 API와 앱 화면을 연결해 문서나 이미지를 처리합니다. 응답 형식, 권한, 오류 처리와 검증 기준까지 함께 구현합니다.',
         '결과물  /  시연할 수 있는 앱 또는 웹 프로토타입'),
    ]):
        top = 254 + i * 158
        guide.rule(top, HexColor('#698470'))
        guide.paragraph(label, top + 10, width=145, size=10, bold=True, color=WARM)
        guide.paragraph(title, top + 36, size=19, leading=26, font='Display', color=PAPER)
        guide.paragraph(description, top + 71, size=11.5, leading=18, width=456, color=SAGE)
        guide.paragraph(result, top + 121, size=9.5, bold=True, color=WARM)
    guide.link('AI를 포함한 과정별 상세 안내', 746, 'course-details', internal=True, dark=True)

    opening(guide, 'architecture', 'AI 응용 서비스  /  사내 규정 안내 도구 설계 예시',
            '직원의 질문에서\n근거 있는 답변까지')
    guide.paragraph('“출장 교통비는 어떻게 정산하나요?” 이 질문 하나를 예로 들어, 자료·AI 모델·업무 화면이 어떤 순서로 연결되는지 설계합니다.',
                    198, size=11.5, leading=20, width=468, color=MUTED)
    guide.box(M + 9, 274, 1, 356, HexColor('#a8b4a1'))
    for i, (layer, name, decision) in enumerate([
        ('자료', '무엇을 근거로 쓸 것인가',
         '승인된 규정만 등록하고 문서명·개정일·열람 권한을 함께 기록합니다. 예전 규정을 현행 기준처럼 사용하지 않도록 합니다.'),
        ('검색', '질문과 관련 있는 조항을 찾는 법',
         '질문자의 열람 범위에서 관련 조항을 찾습니다. 모델에 답변을 요청하기 전에 검색 결과가 적절한지 따로 확인합니다.'),
        ('생성', '찾은 근거를 바탕으로 답변 작성',
         '찾은 조항을 모델에 제공해 답변과 출처를 만듭니다. 이 검색·생성 연결을 RAG라고 부릅니다. 근거가 없으면 답변을 보류합니다.'),
        ('화면', '사람이 확인하고 판단하는 곳',
         '답변에 문서명과 관련 조항을 표시합니다. 예외가 있는 질문은 규정 담당자에게 전달하고, 담당자가 필요할 때 답변을 수정합니다.'),
        ('운영', '규정이 바뀌어도 제대로 답하는지 확인',
         '문서가 갱신되면 대표 질문으로 다시 시험합니다. 근거 누락과 구버전 답변을 기록해 검색 문제인지 생성 문제인지 추적합니다.'),
    ]):
        top = 258 + i * 89
        guide.box(M + 22, top, CONTENT - 22, .55, LINE)
        guide.pdf.setFillColor(CLAY)
        guide.pdf.circle(M + 9.5, H - top - 16, 3.1, fill=1, stroke=0)
        guide.paragraph(layer, top + 10, x=M + 25, width=85, size=10.5, bold=True, color=CLAY)
        guide.paragraph(name, top + 10, x=174, width=367, size=14, font='Display', color=FOREST)
        guide.paragraph(decision, top + 36, x=174, width=367, size=10.5, leading=17, color=MUTED)
    guide.paragraph('문서 관리, 검색, 모델의 응답, 화면 설계는 서로 다른 기술입니다. 각각의 실패 조건을 알아야 전체 도구가 왜 틀렸는지 설명할 수 있습니다.',
                    735, size=10.2, leading=16, width=470, color=MUTED)

    opening(guide, 'evaluation', 'AI 결과 검증과 운영', '잘 만든 답변을 넘어\n일에 써도 되는 결과로')
    guide.paragraph('수업에서는 시연에 쓴 질문과 평가할 질문을 나눕니다. 담당자가 기대 답과 근거를 미리 적어 두고, 실제 결과를 나란히 비교합니다.',
                    206, size=12, leading=21, width=460, color=MUTED)
    guide.box(M, 289, CONTENT, 185, FOREST)
    guide.paragraph('예외 상황  /  오래된 규정과 개정 규정이 함께 검색될 때', 313,
                    x=M + 22, width=CONTENT - 44, size=10.5, bold=True, color=WARM)
    guide.paragraph('AI가 먼저 볼 기준은\n가장 최근의 승인 문서', 350,
                    x=M + 22, width=CONTENT - 44, size=22, leading=29, font='Display', color=PAPER)
    guide.paragraph('최신 여부를 확인할 수 없으면 답을 보류하고 담당자에게 넘깁니다.',
                    426, x=M + 22, width=CONTENT - 44, size=10.5, color=SAGE)
    for i, (title, body) in enumerate([
        ('정확성과 근거', '기대 답과 일치하는지, 제시한 조항이 답변을 실제로 뒷받침하는지 확인합니다.'),
        ('보류와 권한', '근거가 없을 때 보류하는지, 접근이 제한된 자료를 보여주지 않는지 점검합니다.'),
        ('현업의 검토 부담', '기존 방식과 AI를 쓴 방식의 검토 시간·수정 건수를 같은 과제로 비교합니다.'),
    ]):
        x = M + i * 168
        guide.box(x, 516, 152, .7, LINE)
        guide.paragraph(title, 533, x=x, width=151, size=14, font='Display', color=CLAY)
        guide.paragraph(body, 570, x=x, width=147, size=10.5, leading=17, color=MUTED)
    guide.paragraph('AI 에이전트가 자료 조회나 초안 작성까지 맡는다면, 사용할 수 있는 기능을 먼저 정합니다. 외부 발송이나 실제 업무 시스템의 변경은 사람이 승인하도록 설계합니다.',
                    703, size=10.5, leading=17, width=464, color=MUTED)

    opening(guide, 'technology', '분야별 기술 교육', '각 기술을 깊이 알아야\n연결할 곳이 보입니다')
    guide.paragraph('업무에서 풀어야 할 문제를 먼저 살피고, 아래 기술은 각각 독립 실습으로 다루거나 프로젝트 목표에 맞춰 연결합니다.',
                    206, size=12, leading=21, width=470, color=MUTED)
    for i, (title, question, body, evidence) in enumerate([
        ('블록체인', '여러 기관이 같은 이력을 검증하려면',
         '거래 상태와 권한을 설계하고 스마트 계약으로 규칙을 구현합니다. 데이터베이스와 비교해 어떤 조건에서 블록체인을 쓸지 검토합니다.',
         '수업의 근거  /  스마트 계약 모듈 개발과 블록체인 교육'),
        ('모바일 앱', '현장에서 쓰는 화면과 기능을 어떻게 만들까',
         '사용 흐름을 그린 뒤 화면과 서버 API를 연결합니다. 기기 권한, 네트워크 단절, 예외 화면까지 시험합니다.',
         '수업의 근거  /  스마트폰 OS 포팅과 객체 인식 앱 개발'),
        ('IoT', '센서가 읽은 값이 기기 동작이 되기까지',
         '감지 범위와 통신 단절을 확인하고, 장치·서버·운영 화면을 연결합니다. 센서와 조명을 직접 작동시켜 결과를 비교합니다.',
         '수업의 근거  /  IoTPlacement 개발과 대학 실습'),
        ('정보보안', '누가 어떤 데이터와 기능에 접근할 수 있을까',
         '인증과 권한을 구분하고 허용·차단 시나리오를 시험합니다. 개인정보 노출을 줄이는 설계와 운영 기록을 다룹니다.',
         '수업의 근거  /  보안 소프트웨어공학 강의와 NFC 인증 검증'),
    ]):
        x = M + (i % 2) * 251
        top = 278 + (i // 2) * 221
        guide.box(x, top, 236, 201, HexColor('#e6e8d9'))
        guide.paragraph(title, top + 14, x=x + 15, width=204, size=17,
                        leading=24, font='Display', color=FOREST)
        guide.paragraph(question, top + 49, x=x + 15, width=204, size=10.5,
                        leading=16, bold=True, color=CLAY)
        guide.paragraph(body, top + 86, x=x + 15, width=204, size=10.5,
                        leading=17, color=MUTED)
        guide.paragraph(evidence, top + 164, x=x + 15, width=204, size=8.5,
                        leading=13, bold=True, color=FOREST)
    guide.link('교육 과정별 상세 안내', 741, 'course-details', internal=True)

    opening(guide, 'operate', '융합 실습 사례  /  스마트 공간', '센서에서 시작해\n공간이 반응하기까지')
    guide.photograph(PHOTO, M, 224, 319, 192)
    guide.photograph(SENSOR, 390, 224, 151, 91, focus=.65)
    guide.photograph(PAVILION, 390, 325, 151, 91, focus=.60)
    guide.paragraph('왼쪽  /  실제 실습 자료인 IoTPlacement 화면     오른쪽  /  센서와 공간 연출 이미지', 429,
                    size=9, color=MUTED)
    guide.paragraph('감지 → 통신 → 규칙 판단 → 조명 제어 → 상태 확인', 476,
                    size=16, leading=23, font='Display', color=FOREST)
    guide.paragraph('센서가 무엇을 감지하는지, 통신이 끊겼을 때 어떤 상태가 남는지, 운영 화면에서 어떤 값을 확인해야 하는지 따로 시험합니다. 영상으로 사람을 구분해야 하는 과제라면 AI 인식 결과도 다른 조건에서 검증합니다.',
                    526, size=11.5, leading=19, color=MUTED)
    guide.paragraph('가톨릭대학교 AIoT 스마트홈 인테리어 특강에서는 학생들이 공간 시나리오를 설계하고 실제 기기를 연결해 자동화를 실습했습니다.',
                    638, size=10.5, leading=17, color=MUTED)
    guide.link('가톨릭대학교 공식 교육 현장 기사', 724, UNIVERSITY)


    opening(guide, 'letter', '장성균의 편지', '오늘은 여기까지 왔네')
    guide.box(M, 163, 34, 2, CLAY)
    guide.y = 191
    letter = tree('data/mentoring-content.html').xpath('//*[@id="mentor-story"]//p[not(@class="s-eyebrow")]')
    for paragraph in letter:
        closing = 's-mentor-letter-closing' in (paragraph.get('class') or '')
        guide.text(plain(paragraph), size=13.5, leading=24, gap=20,
                   font='Display' if closing else 'Serif', color=GREEN if closing else INK,
                   width=463)


TESTIMONIALS = [
    (2, '나를 위해 시간을 내는 기쁨', '진로를 탐색하던 대학생', (
        '그렇게 진행하다 보니 겨울방학 동안 한 강의를 수료할 수 있었다.',
        '일상 속에 새로운 일정이 생겨나서 정해진 날에는 약속을 안 잡고 나를 위해 시간을 내는 것 같아서 뿌듯하기도 했다.',
        '소토는 신뢰와 책임으로 날 이끌어 주고 좋은 영향을 주셨다.',
        '천천히 이해하며 배우는 게 익숙한 내가 많이 답답할 수 있는데 이해해주시고 처음부터 지금까지 늘 가르쳐주고 싶어 하는 마음이 느껴져서 정말 감사하다.',
    )),
    (6, '조금은 당당하게 출근하는 아침', '백엔드를 배우기 시작한 웹 퍼블리셔', (
        '하지만 멘토를 만나고 어려운 분야임에도 배움이 이렇게 즐겁고 좋은것이구나라고 깨달았습니다.',
        '스스로 학습하기 좋은 습관을 만들어 주셔서 더이상 혼자 공부하는 것이 어렵지 않습니다.',
        '마냥 책 내용 뿐만이 아닌, 실무에 응용할 수 있을 때까지 도와주시는 멘토 덕분에 예전처럼 위축 된 모습이 아닌 조금은 당당하게 출근할 수 있게 되었습니다.',
    )),
    (9, '첫 실무에서 발견한 나', '첫 IT 인턴십에 참여한 멘티', (
        '이전에는 할 수 있는 업무가 없는 나라고 생각했었지만 마지막에는 주어진 업무도 해내는 나를 볼 수 있었다.',
        '이를 통해 처음에는 누구나 모를 수 있으니 주눅들지 않고 자신감을 갖고 꾸준히 나아가다보면 언젠가는 이룰 수 있다는 것을 배웠다.',
        '앞으로도 마음속에 새겨 두고 도전해야겠다고 생각했다.',
    )),
    (13, '어려운 부분을 만날 때 생기는 흥미', '스마트팜을 꿈꾸던 대학생', (
        '이렇게 공부가 기대된 적은 처음이라 신기합니다.',
        '실력 향상 면에서도 소홀히 다루지 않아서 의미가 컸습니다.',
        '제가 어떤 과제를 하면 거기서 멈추지 않고 더 깊은 분야의 정보도 알려주셨고, 제가 스스로 한계를 정할 때면 더 나아갈 수 있음을 알려주시며 멈추고 포기하기보다, 부딪혀볼 것을 독려하였습니다.',
        '그래서인지 요즘에는 어려운 부분을 만나면 흥미가 생기기도 합니다.',
    )),
    (10, '받은 도움을 다음 사람에게', 'AI 졸업작품을 준비한 대학생', (
        '저도 지금의 멘토처럼 나침반같은 역할을 해줄 수 있는 멘토가 되고싶습니다.',
        '자력으로 앞으로 나아갈 수 있게 도움을 주고 싶습니다.',
        '지금의 문제를 파악하고 뚜렷한 목표를 만들도록하고 한 단계씩 문제를 해결해 나가도록 하고 싶습니다.',
        '지금 제가 받은 도움을 그대로 돌려주고 싶다고 느꼈습니다.',
    )),
]


def original_reviews(guide, reviews):
    chosen = []
    for index, title, context, lines in TESTIMONIALS:
        name, original = reviews[index - 1]
        excerpt = ' '.join(lines)
        if excerpt not in original:
            raise ValueError(f'Testimonial {index} does not match the archived text')
        chosen.append((title, f'{name} · {context}', excerpt))

    opening(guide, 'testimonials', '멘토링 소감문', '배움을 다시 시작한 사람들')
    guide.paragraph('이전 멘토링 참가자들이 직접 쓴 소감 중 다섯 편의 일부를 인용했습니다. 제목은 편집했고, 익명 표기는 원문을 따랐습니다.',
                    158, size=10.5, leading=17, width=440, color=MUTED)
    for spread in range(2):
        if spread:
            guide.start()
            guide.paragraph('멘토링 소감문', 53, size=11, bold=True, color=CLAY)
            guide.paragraph('배운 것을 일과 삶으로', 88, size=34, leading=47, font='Display', color=FOREST)
        for column, (title, byline, excerpt) in enumerate(chosen[spread * 2:spread * 2 + 2]):
            top = 226 + column * 263
            guide.rule(top)
            guide.paragraph(title, top + 17, size=22, leading=30, font='Display', color=FOREST)
            guide.paragraph(byline, top + 63, size=10.5, bold=True, color=CLAY)
            guide.paragraph('“' + excerpt + '”', top + 96, width=467, size=13.5,
                            leading=23, font='Serif', color=INK)

    title, byline, excerpt = chosen[4]
    guide.start(dark=True)
    guide.photograph(DESK, 0, 484, W, 357, focus=.48)
    guide.paragraph('멘토링 소감문', 53, size=11, bold=True, color=WARM)
    guide.paragraph(title, 93, size=34, leading=47, font='Display', color=PAPER)
    guide.paragraph(byline, 161, size=11, bold=True, color=WARM)
    guide.paragraph('“' + excerpt + '”', 216, size=17, leading=29, font='Serif',
                    width=467, color=PAPER)



def archive(guide, rows):
    sections = [
        ('research', '연구개발 · 특허와 발명', ('research', 'patent')),
        ('product', '서비스 개발과 운영', ('product',)),
        ('education', '교육·강연과 멘토링 이력', ('education', 'mentoring')),
    ]
    for key, title, categories in sections:
        guide.chapter(key, '활동 기록', title)
        selected = [
            row for category in categories
            for row in sorted((row for row in rows if row['category'] == category),
                              key=lambda row: (re.search(r'\d{4}', row['period']) or ['9999'])[0])
        ]
        entries = [
            (row['title'],
             f"{row['period']}   /   {row['organization']}\n{row['role']}\n{row['result']}\n수업 연결  ·  {row['lesson']}",
             row.get('public_url'), row.get('link_label', '공개 자료 보기'))
            for row in selected
        ]
        record_columns(guide, title, entries)


def record_columns(guide, section, entries):
    width = (CONTENT - 24) / 2
    top = guide.y
    y = top
    column = 0
    for title, body, url, label in entries:
        title_height = guide.paragraph(title, 0, width=width, size=11.5, leading=17,
                                       bold=True, draw=False)
        body_height = guide.paragraph(body, 0, width=width, size=9.5, leading=14.5, draw=False)
        if y + title_height + body_height + (29 if url else 14) > H - 64:
            column += 1
            if column == 2:
                guide.start('상세 이력  /  ' + section)
                top = guide.y
                column = 0
            y = top
        x = M + column * (width + 24)
        guide.box(x, y - 3, width, .55, LINE)
        y += guide.paragraph(title, y + 4, x=x, width=width, size=11.5, leading=17,
                             bold=True, color=FOREST) + 8
        y += guide.paragraph(body, y, x=x, width=width, size=9.5, leading=14.5)
        if url:
            y += guide.link(label, y + 3, url, x=x, width=width) + 3
        y += 15


def reference(guide):
    guide.chapter('career', '교육자 소개', '교육자 경력 · 썬스타 연혁',
                  '장성균 공학박사의 개인 경력과 썬스타·SotoLAB 활동 기록을 담았습니다.')
    profile = tree('profile.html')
    history = tree('history.html')
    entries = [
        (plain(item.xpath('./strong')[0]), plain(item.xpath('./span')[0]), None, '')
        for item in profile.xpath('//*[@id="career"]//ol/li')
    ]
    entries.extend(
        (plain(item.xpath('.//h2')[0]), '\n'.join(plain(node) for node in item.xpath('./span | .//p')), None, '')
        for item in history.xpath('//*[@id="history"]//li[h2 or div/h2]')
    )
    entries.extend(
        (plain(item), '썬스타 설립 이전 활동', None, '')
        for item in history.xpath('//main//section[not(@id)]//li')
    )
    record_columns(guide, '교육자 경력 · 썬스타 연혁', entries)

    guide.start('교육자 경력  /  출강 이력')
    guide.text('기관과 대상별 강의 이력', size=25, font='Display', color=FOREST, gap=20)
    teaching = ([plain(cell) for cell in row.xpath('./td')]
                for row in profile.xpath('//*[@id="teaching"]//tbody/tr'))
    record_columns(guide, '기관과 대상별 강의 이력', [
        (organization, f'{period}   /   {subject}', None, '')
        for period, organization, subject in teaching
    ])

    guide.chapter('books', '수업 자료', '교재와 저서')
    source = tree('books.html')
    entries = []
    for book in source.xpath('//*[@id="publications"]//article'):
        title = plain(book.xpath('.//h2')[0])
        detail = '\n'.join(plain(node) for node in book.xpath('.//p'))
        urls = book.xpath('.//a[starts-with(@href, "https://")][1]/@href')
        entries.append((title, detail, next(iter(urls), None), '자세히 보기'))
    entries.extend(
        (plain(article.xpath('./h3')[0]), '\n'.join(plain(node) for node in article.xpath('./p')), None, '')
        for article in source.xpath('//*[@id="learning-materials"]//*[self::article or self::div][./h3]')
    )
    record_columns(guide, '교재와 저서', entries)

    guide.chapter('course-details', '교육 과정  /  상세 안내', 'AI 응용과 분야별 교육 과정',
                  '시간과 운영 조건은 상담할 때 확인하실 수 있습니다.')
    entries = [
        ('업무 문서에 생성형 AI 적용', '보고서·회의록·문의 메일에서 반복 작업을 고르고, 초안 양식과 사람이 확인할 기준을 설계하는 실습', None, ''),
        ('사내 문서 검색·질의응답', '승인된 문서 등록, 검색, 근거가 있는 답변, 답변 보류와 예외 질문 처리까지 연결하는 실습', None, ''),
        ('AI 앱·웹 서비스 구현', '모델 API를 앱·웹에 연결하고 응답 형식과 권한, 오류 처리, 검증 기준을 설계하는 실습', None, ''),
    ]
    for filename, card_class in [('online.html', 'course-card'), ('curriculum.html', 'sote-step'),
                                 ('mvp-projects.html', 'project-card')]:
        selector = f'//*[contains(concat(" ",normalize-space(@class)," ")," {card_class} ")]'
        for card in tree(filename).xpath(selector):
            titles = card.xpath('.//h2 | .//h3')
            if titles:
                detail = '\n'.join(plain(node) for node in card.xpath('.//p | .//li'))
                entries.append((plain(titles[0]), detail, None, ''))
    record_columns(guide, 'AI 응용과 기업 교육', entries)

    guide.start('교육 과정  /  분야별 실습')
    guide.text('블록체인·모바일 앱·IoT·정보보안', size=24, font='Display',
               color=FOREST, gap=19)
    academy = tree('data/academy-content.html')
    entries = [
        ('모바일 앱 설계와 구현', '사용자 흐름과 화면을 설계하고 API를 연결하며 권한·연결 오류에 대응하는 실습', None, ''),
        ('정보보안 설계 실습', '로그인과 접근 권한, 개인정보 보호, 운영 로그를 설계하고 허용·차단 시나리오를 검증하는 실습', None, ''),
    ]
    entries.extend(
        (plain(entry.xpath('.//h3')[0]),
         '\n'.join(plain(node) for node in entry.xpath('.//p | .//h4 | .//div[@class="s-course-meta"]/span')),
         None, '')
        for entry in academy.xpath('//*[@id="custom-lectures"]//article | //*[@id="courses"]//a[.//h3]')
    )
    record_columns(guide, '분야별 기술 교육', entries)



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
    guide.link('목차와 상세 이력 보기', 682, 'contents', dark=True, internal=True)
    guide.paragraph('표지·작업대·센서·공간 이미지는 교육 맥락을 표현한 연출 이미지입니다.',
                    755, size=9, color=SAGE)


def back_cover(guide):
    guide.start(dark=True)
    guide.photograph(AI_DESK, 0, 0, W, 367, focus=.58)
    guide.paragraph('직접 해온 경험을,\n함께 해내는 배움으로', 446, size=36,
                    leading=52, font='Display', color=PAPER)
    guide.rule(635, HexColor('#758977'))
    guide.paragraph('SotoLAB · 썬스타의 교육·멘토링 브랜드', 662,
                    size=11, color=SAGE)
    guide.link('sotolab.github.io', 710, SITE, width=190, dark=True)
    guide.link('교육 문의', 710, INQUIRY, x=410, width=130, dark=True)


def main():
    guide = Guide()
    reviews = excerpts()
    rows = json.loads((ROOT / 'data/experience.json').read_text(encoding='utf-8-sig'))
    cover(guide)
    story(guide)
    original_reviews(guide, reviews)
    contact(guide)
    contents(guide)
    archive(guide, rows)
    reference(guide)
    back_cover(guide)
    guide.pdf.save()
    print(f'{guide.page} pages, {len(rows)} activity records, {len(TESTIMONIALS)} selected testimonials')


if __name__ == '__main__':
    main()

"""Build SotoLAB's static brand pages from reviewed, public-facing content."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BRAND_ASSET_VERSION = '20261101-6'
ROWS = json.loads((ROOT / 'data/experience.json').read_text(encoding='utf-8'))
MENU = [('profile.html', '강사 소개'), ('academy.html', '교육·강연'), ('sotolab.html', '기업 멘토링'), ('experience.html', '연구·성과'), ('books.html', '저서'), ('contact.html', '문의')]
CATEGORIES = {'education': '교육·강연', 'mentoring': '멘토링', 'research': '연구개발', 'product': '개발 서비스', 'patent': '특허·발명'}
ROWS.sort(key=lambda row: list(CATEGORIES).index(row['category']))
SUBMENUS = {
    'profile.html': [('profile.html#about', '강사 프로필'), ('profile.html#career', '주요 경력'), ('profile.html#teaching', '강의 이력'), ('profile.html#mentoring', '멘토링 철학')],
    'academy.html': [('academy.html#custom-lectures', '맞춤 교육·특강'), ('academy-interior.html', '대학 연계·공간디자인'), ('academy-practice.html', 'AIoT 실습교육'), ('academy-special.html', 'AIoT 실습 연계 교육'), ('academy-visit.html', 'AIoT 방문 교육'), ('academy-business.html', 'AIoT 사업자 교육'), ('reviews.html', '교육 사례')],
    'sotolab.html': [('sotolab.html#framework', 'M2G 프레임워크'), ('online.html', '기업 교육·워크숍'), ('curriculum.html', '도입 방식'), ('sotolab.html#outcomes', '멘토링 결과물'), ('sotolab.html#metrics', '성과 확인 기준'), ('mvp-projects.html', '업무 도구 예시')],
    'experience.html': [('experience.html?category=education#archive-results', '교육·강연 기록'), ('experience.html?category=mentoring#archive-results', '멘토링 기록'), ('experience.html?category=research#archive-results', '연구개발'), ('experience.html?category=product#archive-results', '개발 서비스'), ('experience.html?category=patent#archive-results', '특허·발명')],
    'books.html': [('books.html#publications', '저서·공저'), ('books.html#learning-materials', '실습 교재·설계 도구')],
    'contact.html': [('contact.html#brand-inquiry', '교육·멘토링 문의'), ('contact.html#questions', '문의 전 자주 묻는 질문'), ('https://open.kakao.com/o/sK8hYXfb', '카카오톡 상담'), ('mailto:sotolabedu@gmail.com', '이메일 문의')],
}


def nav(page):
    items = []
    for index, (url, label) in enumerate(MENU):
        current = ' aria-current="page"' if url == page else ''
        links = [(url, label + ' 전체 보기')] + SUBMENUS[url]
        submenu = ''.join(f'<li><a href="{escape(href, quote=True)}"' + (' target="_blank" rel="noopener noreferrer"' if href.startswith('https:') else '') + f'>{escape(text)}</a></li>' for href, text in links)
        items.append(f'<li><details class="s-nav-group" name="brand-navigation"><summary{current} aria-controls="brand-submenu-{index}">{label}<span aria-hidden="true">⌄</span></summary><ul class="s-submenu" id="brand-submenu-{index}" aria-label="{label} 하위 메뉴">{submenu}</ul></details></li>')
    header = f'<a class="s-skip" href="#main">본문으로 이동</a><header class="s-header"><nav class="s-wrap s-nav" aria-label="주요 메뉴"><a class="s-logo" href="index.html" aria-label="SotoLAB 홈">Soto<b>LAB</b></a><button class="s-menu-toggle" id="brand-menu-toggle" type="button" aria-expanded="false" aria-controls="brand-menu">메뉴</button><ul id="brand-menu" class="s-menu">{"".join(items)}</ul></nav></header>'
    return '<!-- SOTOLAB_NAV_START -->' + header + '<!-- SOTOLAB_NAV_END -->'


def footer():
    return '''<footer class="s-footer"><div class="s-wrap"><div class="s-footer-top"><div><a class="s-logo" href="index.html">Soto<b>LAB</b></a><p>직접 만든 기술을, 사람의 실력으로<br>AI · AIoT · 임베디드 · 블록체인 실전 교육과 멘토링</p></div><div class="s-footer-links"><a href="profile.html">장성균 박사 소개</a><a href="experience.html">활동·성과 기록</a><a href="books.html">저서</a><a href="contact.html">교육·강연 문의</a></div></div><div class="s-footer-bottom"><span>© 2026 SotoLAB · All rights reserved</span><span>운영: 썬스타 · 문의: <a href="mailto:sotolabedu@gmail.com">sotolabedu@gmail.com</a></span></div></div></footer>'''


def page(filename, title, description, body):
    canonical = 'https://sotolab.github.io/' + ('' if filename == 'index.html' else filename)
    schema = ''
    if filename in ('index.html', 'profile.html'):
        person = {'@context': 'https://schema.org', '@type': 'Person', 'name': '장성균', 'alternateName': 'SOTO', 'url': 'https://sotolab.github.io/profile.html', 'jobTitle': 'AI·AIoT 실전 교육자', 'knowsAbout': ['인공지능', '사물인터넷', '임베디드 시스템', '블록체인', '기술 멘토링'], 'alumniOf': {'@type': 'CollegeOrUniversity', 'name': '한양대학교'}}
        schema = '<script type="application/ld+json">' + json.dumps(person, ensure_ascii=False) + '</script>'
    html = f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | SotoLAB</title><meta name="description" content="{escape(description, quote=True)}"><meta name="author" content="장성균 · SotoLAB"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(title, quote=True)} | SotoLAB"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="SotoLAB"><meta property="og:image" content="https://sotolab.github.io/img/logo.png"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title, quote=True)} | SotoLAB"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="https://sotolab.github.io/img/logo.png"><meta name="theme-color" content="#0c110e"><link rel="icon" href="img/favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="css/sotolab-brand.css?v={BRAND_ASSET_VERSION}"><script src="js/sotolab-brand.js?v={BRAND_ASSET_VERSION}" defer></script><script src="js/sotolab-space.js?v={BRAND_ASSET_VERSION}" defer></script><script src="js/sotolab-scroll.js?v={BRAND_ASSET_VERSION}" defer></script></head><body class="story-page">{nav(filename)}<main id="main">{body}</main>{footer()}</body></html>'''
    html = html.replace('</head>', schema + '<noscript><style>.s-menu{display:flex!important}.s-menu-toggle{display:none!important}</style></noscript></head>')
    (ROOT / filename).write_text(html + '\n', encoding='utf-8')


def heading(kicker, title, description=''):
    return f'<div class="s-section-heading"><div><p class="s-eyebrow">{kicker}</p><h2>{title}</h2></div>' + (f'<p>{description}</p>' if description else '') + '</div>'


def cta():
    return '''<section class="s-cta"><div class="s-wrap"><p class="s-eyebrow">LET’S BUILD THE NEXT CLASS</p><h2>다음 교육이,<br>실제 변화의 시작이 되도록</h2><p>기관과 대상, 관심 기술과 교육 목표를 알려 주세요.<br>강연부터 실습, 프로젝트 멘토링까지 함께 설계합니다.</p><div class="s-actions"><a class="s-button s-button-primary" href="contact.html">교육·강연 문의하기 ↗</a><a class="s-button" href="sotolab.html">기업 멘토링 살펴보기 →</a></div></div></section>'''


def record(row, i):
    cat = row['category']
    dl = ''.join(f'<dt>{label}</dt><dd>{escape(row[key])}</dd>' for label, key in [('역할', 'role'), ('결과', 'result'), ('수업 연결', 'lesson')])
    link = f'<a class="s-text-link" href="{escape(row["public_url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(row["link_label"])}</a>' if row.get('public_url') else ''
    return f'''<article class="s-record" data-category="{cat}" id="record-{i}"><div class="s-record-top"><span>{CATEGORIES[cat]}</span><span>{escape(row['period'])}</span></div><h2>{escape(row['title'])}</h2><p>{escape(row['organization'])}</p><dl>{dl}</dl>{link}</article>'''


def build_home():
    body = '''<section class="s-hero"><div class="s-wrap"><div class="s-hero-grid"><div><p class="s-eyebrow">SOTOLAB / BUILD · TEACH · MENTOR</p><h1>현장에서 만든 기술을,<br><em>사람의 실력으로</em></h1><p class="s-lead">AI·AIoT 실전 교육자 장성균 박사<br>임베디드 개발부터 AI 서비스와 스마트 공간까지, 직접 연구하고 개발한 경험을 교육과 멘토링으로 연결합니다.</p><div class="s-actions"><a class="s-button s-button-primary" href="contact.html">강연·교육 문의하기 ↗</a><a class="s-button" href="experience.html">해온 일과 결과 보기 →</a></div><p class="s-hero-note">기업 실무자 · 대학·대학원 · 공공기관 · 창업팀을 위한 맞춤 교육</p></div><figure class="s-hero-art"><div class="s-art-top"><span>FROM THE LAB TO THE CLASSROOM</span><span>01 / AIoT</span></div><img src="img/academy-simulator-3d.png" alt="SotoLAB의 IoTPlacement 3D 공간 설계 시뮬레이터 예시" width="680" height="386"><figcaption class="s-art-caption"><strong>설명하는 기술에, 만든 경험을 더합니다.</strong><p>직접 개발한 IoTPlacement로 장치 배치와 공간 설계를 수업의 실습 도구로 연결합니다.</p></figcaption></figure></div><div class="s-facts"><div class="s-fact"><strong>2002</strong><span>임베디드 실무 경력의 시작</span></div><div class="s-fact"><strong>2009</strong><span>IT 프로젝트 멘토링 수행</span></div><div class="s-fact"><strong>2013</strong><span>한컴아카데미 전문 교육</span></div><div class="s-fact"><strong data-count-to="7">7권</strong><span>기술·멘토링 저서와 공저</span></div></div></div></section>
<section class="s-section s-section-tint"><div class="s-wrap">'''
    body += heading('01 / YOUR INSTRUCTOR', '개발자, 연구자,<br>그리고 끝까지 함께하는 교육자', '기술을 실제로 만드는 경험과 학습자의 성장을 돕는 경험 · 두 가지를 함께 쌓아 왔습니다.')
    body += '''<div class="s-person s-person-text"><div><h2>장성균 <small>AI·AIoT 실전 교육 · 기술 멘토</small></h2><p>스마트폰 OS와 임베디드 시스템을 개발하고, IoT 플랫폼과 블록체인 서비스를 연구했습니다. 달 탐사 통신 소프트웨어, 자원순환 AIoT, 시니어 케어 등 여러 현장에서 기술이 실제로 쓰이는 과정을 경험했습니다.</p><p>그 경험을 기업 개발자와 재직자, 대학생, 창업자, 농업인에게 전해 왔습니다. SotoLAB의 수업은 원리를 이해하고 직접 구현하며, 자신의 문제에 적용하는 과정을 지향합니다.</p><div class="s-credentials"><div>한양대학교 공학박사<small>컴퓨터소프트웨어 · 2020년 학위 취득</small></div><div>한컴아카데미 전문 교육 경력<small>AI·IoT·블록체인·임베디드 과정 개발 및 강의</small></div><div>대학과 산업 현장을 잇는 교육<small>한양대 겸임교수·한양사이버대 비전임 교수 역임</small></div><div>연구개발과 서비스 구축 경험<small>플랫폼·장치·앱·클라우드를 연결하는 실무</small></div></div><a class="s-text-link" href="profile.html">강사 소개와 전체 경력 보기 →</a></div></div></div></section>
<section class="s-section" id="programs"><div class="s-wrap">'''
    body += heading('02 / LEARNING THAT CONNECTS', '기술을 이해하고,<br>자신의 결과물을 만드는 수업', '특강, 집중 실습, 학기 연계, 기업 멘토링 · 대상자의 수준과 끝내 도달할 결과에서 교육을 설계합니다.')
    programs = [
        ('01 / AI & WORK', 'AI 활용 · 기업 멘토링', '생성형 AI를 업무에 적용하고, 반복 업무를 줄이는 도구를 만들어 봅니다.', ['대상: 기업 재직자·팀 리더·실무자', '주제: AI 업무 적용, 업무 도구, 자동화', '학습 목표: 자신의 업무 과제와 실행 계획'], 'sotolab.html', '기업 멘토링'),
        ('02 / AIoT & SPACE', 'AIoT · 스마트 공간 실습', '센서와 조명을 직접 연결하고, 사용자 행동에 반응하는 공간을 설계합니다.', ['대상: 공간디자인 전공·현업·기관', '주제: 장치 연결, 공간 배치, 자동화', '학습 목표: 공간 시나리오와 동작 검증'], 'academy.html', '아카데미'),
        ('03 / ENGINEERING', '임베디드 · 블록체인 · 기술 강연', '디바이스와 플랫폼의 원리를 배우고, 구현 사례로 시스템의 구조를 이해합니다.', ['대상: 개발자·대학생·공공기관·창업팀', '주제: 임베디드, IoT 플랫폼, 블록체인', '학습 목표: 구조 이해와 프로젝트 방향'], 'contact.html', '맞춤 강연 상담')]
    body += '<div class="s-grid-3">'
    for n, title, desc, points, url, link in programs:
        body += f'<article class="s-card"><span class="s-card-number">{n}</span><h3>{title}</h3><p>{desc}</p><ul>' + ''.join(f'<li>{p}</li>' for p in points) + f'</ul><a class="s-text-link" href="{url}">{link} →</a></article>'
    body += '</div><p class="s-small">온라인에서도 수업을 만나보세요. <a class="s-text-link" href="https://www.inflearn.com/course/블록체인-이해-구조" target="_blank" rel="noopener noreferrer">인프런의 장박사 블록체인 강의·수강평 보기 ↗</a></p></div></section><section class="s-section s-section-tint" id="research"><div class="s-wrap">'
    body += heading('03 / EXPERIENCE INTO EVIDENCE', '어떤 일을 했고,<br>무엇으로 남겼는가', '과제별 역할과 결과를 살펴보세요. 개인의 실무·연구 참여와 SotoLAB의 개발·교육 사례를 함께 기록합니다.')
    body += '''<div class="s-grid-3"><article class="s-card"><span class="s-card-number">RESEARCH / 2015–2017</span><h3>달 탐사 통신<br>소프트웨어 포팅</h3><p>ETRI의 DTN 시험환경과 기능 검증 플랫폼, 지상노드 제작 과제에서 임베디드 소프트웨어 포팅 업무를 맡았습니다.</p><p class="s-outcome">수업으로 연결: 통신 제약, 실행 환경, 시스템 검증을 함께 생각하는 개발 관점</p><a class="s-text-link" href="experience.html?category=research#archive-results">연구개발 이력 보기 →</a></article><article class="s-card"><span class="s-card-number">FIELD / 2020–2023</span><h3>자원순환 AIoT와<br>시니어 케어</h3><p>폐플라스틱 회수의 장치·웹·앱 연동, 시범운영 데이터 분석, 사회약자 안전 모니터링 구축과 실증에 참여했습니다.</p><p class="s-outcome">수업으로 연결: 장치가 작동한 뒤 사용자의 생활과 서비스 운영까지 살펴보는 시각</p><a class="s-text-link" href="experience.html?category=research#archive-results">역할과 결과 살펴보기 →</a></article><article class="s-card s-card-image"><img src="img/academy-simulator-plan.png" alt="IoTPlacement 평면 장치 배치 도구 예시" loading="lazy"><div class="s-card-body"><span class="s-card-number">PRODUCT / IoTPLACEMENT</span><h3>직접 만든 도구로<br>더 깊어지는 실습</h3><p>공간 설계·장치 배치·AI 검수를 연결하는 IoTPlacement · 개발 경험을 실제 수업과 반복 학습에 활용합니다.</p><a class="s-text-link" href="experience.html?category=product#archive-results">개발 서비스 보기 →</a></div></article></div><div class="s-actions"><a class="s-button" href="experience.html">교육·멘토링·연구·발명 전체 기록 보기 →</a><a class="s-button" href="books.html">지식으로 남긴 저서 보기 →</a></div></div></section>
<section class="s-section"><div class="s-wrap">'''
    body += heading('04 / HOW I TEACH', '알게 되는 순간에서,<br>스스로 해내는 순간까지', '질문하고, 만들고, 검증하고, 다시 적용합니다. 수업의 마지막에는 다음 행동이 남도록 합니다.')
    steps = [('01', '문제에서 출발', '누구를 위해 무엇을 만들지, 지금 업무와 전공에서 필요한 질문을 정합니다.'), ('02', '원리를 연결', '용어와 개념을 장치·데이터·서비스의 전체 흐름 안에서 이해합니다.'), ('03', '직접 구현·검증', '작은 기능을 만들고 예상과 다른 동작을 확인하며 개선합니다.'), ('04', '자기 일에 적용', '결과를 설명하고, 자신의 업무·설계·프로젝트로 확장할 계획을 세웁니다.')]
    body += '<div class="s-steps">' + ''.join(f'<article class="s-step"><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n,t,d in steps) + '</div></div></section>'
    body += '''<section class="s-section s-section-tint"><div class="s-wrap s-split"><div><p class="s-eyebrow">05 / UNIVERSITY FIELD NOTE</p><h2 style="font-size:36px">전공의 아이디어가<br>스마트 공간으로 이어지다</h2><p class="s-intro">2026년 가톨릭대학교 AIoT 스마트홈 인테리어 특강 · 공간과 기술이 만나는 실제 교육 사례입니다.</p><a class="s-text-link" href="https://www.catholic.ac.kr/ko/newsroom/photonews.do?mode=view&amp;articleNo=274897" target="_blank" rel="noopener noreferrer">가톨릭대학교 공식 기사 보기 ↗</a></div><div class="s-callout"><span class="s-tag">2026.08.11–12</span><span class="s-tag">관련 전공 학생 30명</span><h3>공간 시나리오 설계부터<br>실제 기기 자동화까지</h3><p>학생들이 공간의 사용 장면을 생각하고 실제 IoT 장치로 구현하는 교육을 진행했습니다. 대학 공식 뉴스룸에 자동화 실습과 쇼룸 체험이 소개됐습니다.</p><a class="s-button" href="academy-interior.html">대학 연계 교육 구성 보기 →</a><p class="s-small">위 내용은 기존 운영 사례입니다. 현재 대학 연계 상품의 실습은 회당 최대 15명이며, 쇼룸 방문은 별도 협의합니다.</p></div></div></section>'''
    page('index.html', 'AI·AIoT 실전 교육자 장성균', '임베디드 개발, IoT 플랫폼, AI·블록체인 연구 경험을 교육과 멘토링으로 연결합니다. SotoLAB 장성균 박사의 강의·연구·개발·저서를 만나보세요.', body + cta())


def build_profile():
    body = '''<section class="s-page-head"><div class="s-wrap"><p class="s-eyebrow">THE PRACTITIONER WHO TEACHES</p><h1>만들어 본 기술을,<br>함께 성장하는 배움으로</h1><p>AI·AIoT 실전 교육자 장성균 박사 · 개발 현장의 문제를 연구하고, 그 경험을 이해할 수 있는 언어와 직접 해보는 실습으로 바꿉니다.</p><div class="s-subnav"><a href="#about">강사 소개</a><a href="#career">경력</a><a href="#teaching">강의 이력</a><a href="#mentoring">멘토링 철학</a><a href="experience.html">활동·성과 기록 →</a></div></div></section><section class="s-section s-section-tint" id="about"><div class="s-wrap s-person s-person-text"><div><p class="s-eyebrow">ENGINEER · RESEARCHER · EDUCATOR</p><h2>장성균 <small>직접 만든 기술을, 사람의 실력으로</small></h2><p>2002년부터 임베디드 시스템과 스마트폰 OS 개발 현장을 경험했습니다. 이후 IoT 플랫폼, 보안, 블록체인, 머신러닝으로 연구와 개발의 범위를 넓혔습니다. 한양대학교에서 컴퓨터소프트웨어 전공 공학박사 학위를 취득했습니다.</p><p>달 탐사 DTN 소프트웨어 포팅, 스마트 장치 개발, 자원순환 AIoT, 시니어 케어와 플랫폼 서비스까지 · 개별 기술이 실제 환경에서 연결되고 검증되는 일을 해 왔습니다.</p><p>기업 개발자와 재직자, 대학·대학원생, 공공부문 실무자, 창업자와 농업인을 대상으로 교육하고 멘토링했습니다. 학습자의 배경에 맞춰 기술을 풀어내고, 스스로 만들어 볼 수 있는 과정으로 연결합니다.</p><div class="s-credentials"><div>한양대학교 공학박사<small>컴퓨터소프트웨어 · 2020.02</small></div><div>한양대학교 공학석사<small>컴퓨터공학 · 2009.08</small></div><div>동명대학교 공학사<small>컴퓨터공학 · 2002.02</small></div><div>관심·교육 분야<small>AI·AIoT, 임베디드, 보안, 블록체인</small></div></div></div></div></section><section class="s-section" id="career"><div class="s-wrap">'''
    body += heading('01 / CAREER', '현장의 경험이 쌓여,<br>수업의 깊이가 되었습니다.')
    career = [('2002–2012', '한컴MDS', '임베디드 시스템 개발·스마트폰 OS 포팅'), ('2013–2015', 'MNI Lab', 'IoT 플랫폼 설계·연구개발'), ('2013년부터', '한컴아카데미 전문 교육', 'AI·IoT·블록체인·임베디드·통신 과정 개발 및 강의'), ('2015년부터', '썬스타 · SotoLAB 활동', '기술 개발, 교육 콘텐츠, 멘토링 서비스 · 2018년 SotoLAB 회사소개서에 교육·컨설팅·개발 사업 수록'), ('교수 경력', '한양대학교 · 한양사이버대학교', '공학대학원 겸임교수·해킹보안 분야 비전임 교수 역임'), ('2017–2019', '블로코', '사외 교육전담 이사'), ('2021–2022', '디오비스튜디오', 'AI 버추얼휴먼 분야 사외 기술이사'), ('2021.12–2025.04', '아카라라이프', 'AIoT 관련 기술지원 이사·연구개발 및 교육'), ('2025–2026', '디지털 콘텐츠 연구개발', '비가청 주파수 워터마크 기반 디지털 콘텐츠 마켓 과제 총괄 이력'), ('현재의 SotoLAB', '기술 교육·강연·기업 멘토링', '실무와 연구에서 얻은 경험을 학습자의 구현과 적용으로 연결')]
    body += '<ol class="s-list">' + ''.join(f'<li><span class="s-period">{date}</span><strong>{name}</strong><span>{desc}</span></li>' for date,name,desc in career) + '</ol><p class="s-small">대표 개인의 경력과 참여 프로젝트를 포함합니다. 기관명은 재직·출강·참여 이력을 설명하며 현재의 제휴 관계를 뜻하지 않습니다.</p></div></section><section class="s-section s-section-tint" id="teaching"><div class="s-wrap">'
    body += heading('02 / TEACHING EXPERIENCE', '대상은 달라도,<br>스스로 해내는 수업이라는 기준')
    body += '<div class="s-table-wrap"><table class="s-table"><thead><tr><th scope="col">시기</th><th scope="col">기관·대상</th><th scope="col">강의·교육 내용</th></tr></thead><tbody>'
    courses = [('2005–2010', 'LG 아카데미·삼성전자 상생협력아카데미', '개발자 대상 임베디드 SW'), ('2013–2022', '한컴MDS·한컴아카데미', 'IoT·AI·블록체인·임베디드·통신'), ('2015–2017', '한양대학교 공학대학원', '소프트웨어공학·시스템 설계'), ('2016–2023', '한양사이버대학교', '보안 소프트웨어공학'), ('2017–2020', '한국인터넷진흥원 핀테크아카데미', '블록체인 개요·실습'), ('2017–2018', 'KT DS·KB데이터시스템 등', '기업 재직자 대상 블록체인 구조'), ('2018–2020', '강원·대구 창조경제혁신센터·아트센터 나비', '블록체인 개발·프로젝트 멘토링'), ('2019–2022', 'ETRI·경북SW융합진흥센터·제주산학융합원', '블록체인 개발·클라우드 컴퓨팅'), ('2019년부터', '한국전파진흥협회', '공공부문을 위한 신기술·블록체인'), ('2020–2022', '제주ICT 협동조합·서귀포농업기술센터', '농업인 대상 스마트팜'), ('2025–2026', '한국지능형사물인터넷협회·IoT 융합센터', 'IoT 인테리어 실무'), ('2026.08', '가톨릭대학교 관련 전공 학생', 'AIoT 스마트홈 인테리어 실습 특강')]
    body += ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a,b,c in courses) + '</tbody></table></div><p class="s-small">강의확인서, 경력증명서, 강사 이력(2026.04), 최신 이력서(2026.10), 대학 공식 교육 기사에 근거해 정리했습니다. 학기·과정별 세부 기간은 교육 이력에 포함된 대표 기간입니다.</p><a class="s-text-link" href="experience.html?category=education#archive-results">교육별 역할과 결과 보기 →</a></div></section><section class="s-section" id="mentoring"><div class="s-wrap s-split"><div><p class="s-eyebrow">03 / MENTORING PHILOSOPHY</p><h2 style="font-size:36px">배운 사람이,<br>다음 사람의 멘토가 되도록</h2><p class="s-intro">2009–2010년 IT 멘토링 수행확인서에는 위치기반 서비스, 안드로이드·웹 서비스, 근전도 디바이스 제어 프로젝트가 기록되어 있습니다. 스마트벤처창업학교와 창작·창업 현장에서도 기술 멘토로 함께했습니다.</p><p class="s-intro">『멘토티 멘토링』에는 멘토와 멘티가 경험을 나누고, 협업하며, 다음 사람의 성장을 돕는다는 철학을 담았습니다.</p></div><div><blockquote class="s-quote">기술을 가르치는 일은<br>한 사람이 다음 도전을<br>시작하도록 돕는 일입니다.</blockquote><p class="s-intro">SotoLAB은 국내 기술 교육 현장에서 믿고 찾을 수 있는 교육·멘토링 브랜드를 지향합니다. 그 신뢰를 만드는 기준은 직접 해 본 경험, 이해할 수 있는 설명, 끝까지 확인하는 실습입니다.</p><a class="s-text-link" href="books.html">저서와 교육 자료 보기 →</a></div></div></section>'
    page('profile.html', '장성균 박사 소개 · 강의와 기술 경력', '장성균 박사의 개발·연구·강의·멘토링 이력 · 한컴MDS, 대학 교육, AIoT 실무와 프로젝트 경험을 소개합니다.', body + cta())


def build_experience():
    filters = '<button type="button" class="s-filter" data-archive-filter="all" aria-pressed="true">전체</button>' + ''.join(f'<button type="button" class="s-filter" data-archive-filter="{key}" aria-pressed="false">{label}</button>' for key,label in CATEGORIES.items())
    body = f'''<section class="s-page-head"><div class="s-wrap"><p class="s-eyebrow">SOTOLAB EXPERIENCE ARCHIVE</p><h1>해온 일과,<br>그 일이 남긴 결과</h1><p class="s-archive-total"><strong data-count-to="{len(ROWS)}">{len(ROWS)}</strong>개의 활동 기록</p><p>교육, 멘토링, 연구개발, 서비스와 발명 · 장성균 박사의 개인 경력과 SotoLAB의 활동을 분야별로 모았습니다. 역할과 결과, 그리고 그 경험이 교육에 어떻게 연결되는지 살펴보세요.</p><p class="s-small">기관 발급 확인서·프로젝트 보고서·이력서·포트폴리오에 근거한 기록입니다. 수행기관의 공동 성과와 개인의 참여 역할을 구분하고, 출원·초안·등록 이력은 각각의 근거에 맞춰 표시했습니다.</p></div></section><section class="s-section" id="archive-results" aria-labelledby="archive-title" style="padding-top:20px"><div class="s-wrap"><h2 class="s-content-title" id="archive-title" tabindex="-1">전체 활동 기록</h2><div class="s-filter-bar"><div class="s-filters" role="group" aria-label="활동 분야 선택">{filters}</div><label class="s-search" for="archive-search">기록 검색<input id="archive-search" type="search" placeholder="예: IoT, 멘토링, 한컴, 달 탐사"></label></div><p class="s-result-count" id="archive-count" role="status" aria-live="polite">총 {len(ROWS)}개 활동 기록</p><noscript><p class="s-small">검색과 분야 필터는 JavaScript 사용 시 제공됩니다. 아래에서 전체 기록을 읽을 수 있습니다.</p></noscript><div class="s-archive">'''
    body += ''.join(record(row,i+1) for i,row in enumerate(ROWS))
    body += '</div><div class="s-empty" id="archive-empty" hidden><p>검색 조건에 맞는 기록이 없습니다.</p><button type="button" class="s-button" id="archive-reset">전체 기록 다시 보기</button></div><p class="s-small">기록 정리 기준: 2026.10.31 · 포트폴리오의 소개 시점은 실제 개발 완료 연도와 다를 수 있습니다. 과거의 활동은 현재의 운영·제휴·특허 권리 상태를 뜻하지 않습니다.</p></div></section>'
    page('experience.html', '교육·멘토링·연구개발 · 활동과 성과 기록', '교육·강연, 기술 멘토링, 달 탐사 통신, IoT·AI 플랫폼, 블록체인과 특허·발명까지 · 역할과 결과를 연결한 활동 기록입니다.', body + cta())


def build_books():
    books = [('2011', '임베디드 스케치', '코너북', '임베디드 소프트웨어의 개발 경험을 정리한 기술서', '임베디드 SW'), ('2016', '임베디드 소프트웨어 개발 실무론', '코너북', '임베디드 소프트웨어 개발의 실무 관점을 담은 기술서', '개발 실무'), ('2018', '블록체인으로 구축하는 투표시스템', '사도출판 · 공저 · 전자책', '구름IDE와 Ruby on Rails를 활용한 이더리움 기반 개발의 입문 가이드', '블록체인 구현'), ('2018', '오늘부터 나도 미니컴퓨터 메이커', '바이플러그 · 공저', '미니컴퓨터와 사물인터넷 디바이스를 직접 다루는 메이커 교육', '만들며 배우기'), ('2019', '오늘부터 나도 블록체인 앱 메이커', '바이플러그 · 공저', '블록체인 전자지갑과 앱을 구현하며 기술을 이해하는 교육', '앱 개발 실습'), ('2019', '블록체인 멘토링', '소토에듀 · 공저', '블록체인 기반 기술과 개발 방법을 안내하는 가이드', '기술 멘토링'), ('2022', '멘토티 멘토링', '소토에듀', '개발자의 성장과 멘토·멘티의 경험을 담은 멘토링 이야기', '성장과 연결')]
    body = '''<section class="s-page-head"><div class="s-wrap"><p class="s-eyebrow">BOOKS & LEARNING MATERIALS</p><h1>경험을 기록하고,<br>다음 사람의 배움으로</h1><p>임베디드에서 블록체인, 메이커 교육과 멘토링까지 · 장성균 박사의 저서·공저 7종과 실습 교육 자료를 소개합니다.</p></div></section><section class="s-section" id="publications" style="padding-top:0"><div class="s-wrap s-book-list">'''
    body += ''.join(f'<article class="s-book"><div><span class="s-tag">{tag}</span><h2>{title}</h2><p>{desc}</p></div><div class="s-book-meta">{year}<span>{publisher}</span></div></article>' for year,title,publisher,desc,tag in books)
    body += '''<p class="s-small">저서 목록은 강사 이력(2026.04)·최신 이력서(2026.10)·보관 원고와 표지 자료를 바탕으로 정리했습니다. 개정·인쇄 시점에 따라 차이가 있는 발행월은 생략했습니다.</p></div></section><section class="s-section s-section-tint" id="learning-materials"><div class="s-wrap">'''
    body += heading('LEARNING MATERIALS', '수업이 끝난 뒤에도,<br>다시 따라가 볼 수 있도록', '교육 현장에서 사용하는 자료와 직접 개발한 도구를 함께 연결합니다.')
    body += '''<div class="s-split"><div class="s-person"><figure class="s-portrait"><img src="img/academy-cover-iot-interior.png" alt="AIoT 인테리어 실습 교육 교재 표지" loading="lazy" style="height:auto"></figure><div><h3>AIoT 인테리어 실습 교육 교재</h3><p>공간 시나리오와 장치 배치, 센서·조명 연결, 앱 설정과 자동화까지 직접 따라가는 실습 자료입니다.</p><a class="s-text-link" href="academy-interior.html">교재·대학 연계 교육 상세 →</a></div></div><div class="s-callout"><span class="s-tag">IoTPlacement</span><h3>설계 도구가 되는 실습 환경</h3><p>평면과 3D 공간에서 IoT 장치의 위치와 조명 배치를 살펴봅니다. 배운 내용을 자신의 공간 설계에 다시 적용할 수 있도록 돕습니다.</p><a class="s-text-link" href="https://iotplacement.com" target="_blank" rel="noopener noreferrer">IoTPlacement 살펴보기 ↗</a><p class="s-small">교재 제공 범위와 도구 이용 조건은 교육 제안 시 안내합니다.</p></div></div></div></section>'''
    page('books.html', '저서·공저와 실습 교육 자료', '임베디드 스케치, 임베디드 소프트웨어 개발 실무론, 미니컴퓨터·블록체인 메이커, 블록체인 멘토링, 멘토티 멘토링 등 장성균 박사의 저서와 교재', body + cta())


def build_contact():
    body = '''<section class="s-page-head"><div class="s-wrap"><p class="s-eyebrow">INVITE SOTOLAB</p><h1>어떤 변화를 위한<br>교육을 준비하고 계신가요?</h1><p>기관 특강, 기업 실습교육, 대학 연계, 프로젝트 멘토링까지 · 대상자와 목표를 먼저 이해하고 교육의 구성과 깊이를 제안합니다.</p></div></section><section class="s-section" style="padding-top:20px"><div class="s-wrap s-split"><div><p class="s-eyebrow">EDUCATION · LECTURE · MENTORING</p><h2 style="font-size:34px">목표와 대상에 맞춰,<br>시작점을 함께 찾습니다.</h2><ul class="s-list"><li><strong>기업·공공기관</strong><span>AI 업무 적용, 기술 이해 특강, 실습 워크숍, 업무 도구 제작 멘토링</span></li><li><strong>대학·교육기관</strong><span>AI·AIoT·임베디드·블록체인 교육, 공간디자인 연계 실습, 캡스톤 자문</span></li><li><strong>창업팀·프로젝트팀</strong><span>기술 기획 검토, 구현 우선순위, 시제품과 서비스 구조 멘토링</span></li></ul><div class="s-actions"><a class="s-button s-button-primary" href="https://open.kakao.com/o/sK8hYXfb" target="_blank" rel="noopener noreferrer">카카오톡 상담창 ↗</a><a class="s-button" href="mailto:sotolabedu@gmail.com">이메일로 문의 →</a></div><p class="s-small">sotolabedu@gmail.com<br>오른쪽 양식으로 문의 내용을 정리한 뒤 상담창이나 이메일로 보내 주세요.</p></div><form class="s-form" id="brand-inquiry"><h2>문의 내용 준비하기</h2><p class="s-small" style="margin-top:0">입력한 내용은 전송·저장되지 않습니다. 복사 후 상담 채널로 보내 주세요.</p><fieldset id="brand-inquiry-fields" disabled><div class="s-form-grid"><label>기관·담당자<input name="organization" maxlength="100" placeholder="예: ○○대학교 / 교육 담당자"></label><label>문의 유형<select name="type"><option>교육·특강</option><option>기업 AI 멘토링</option><option>대학 연계 AIoT 교육</option><option>기술·프로젝트 멘토링</option><option>기타 협업</option></select></label><label>교육 대상·인원<input name="audience" maxlength="120" placeholder="예: 공간디자인 전공 학생 30명"></label><label>희망 일정<input name="schedule" maxlength="100" placeholder="예: 2027년 1학기 / 일정 협의"></label></div><label>교육 목표·관심 주제<textarea name="goal" rows="3" maxlength="1500" placeholder="배운 뒤 할 수 있기를 바라는 일, 현재 수준과 고민을 알려 주세요."></textarea></label><label>복사할 문의 내용<textarea id="brand-inquiry-summary" rows="7" readonly></textarea></label><button class="s-button s-button-primary" type="submit">문의 내용 복사하기 →</button><p class="s-copy-status" id="brand-copy-status" role="status" aria-live="polite"></p></fieldset><noscript><p class="s-small">문의 내용 복사 양식은 JavaScript 사용 시 이용할 수 있습니다. 왼쪽 카카오톡 또는 이메일로 직접 문의해 주세요.</p></noscript></form></div></section><section class="s-section s-section-tint" id="questions"><div class="s-wrap">'''
    body += heading('BEFORE WE START', '문의 전 살펴보세요.')
    faqs = [('교육 내용과 시간은 정해져 있나요?', '아카데미의 정규 과정은 각 상세 페이지에서 확인할 수 있습니다. 기관 특강과 맞춤 교육은 대상·목표·일정·실습 환경을 확인한 뒤 구성합니다.'), ('비개발자와 전공자가 함께 참여할 수 있나요?', '가능합니다. 기초 이해와 실습 난이도를 대상에 맞춰 협의합니다. 개발자 과정은 구현과 구조 검토에, 비개발자 과정은 활용 장면과 직접 경험하는 실습에 무게를 둡니다.'), ('강의에서 다룬 내용을 실제 프로젝트로 확장할 수 있나요?', '프로젝트 기획, 장치·서비스 구성, 구현 우선순위와 동작 검증까지 후속 멘토링 범위를 협의할 수 있습니다. 지원 일정과 산출물은 제안 단계에서 정합니다.'), ('강사 경력과 교육 사례를 먼저 볼 수 있나요?', '강사 소개에서 경력과 출강 이력을, 연구·성과에서 활동별 역할과 결과를 확인하실 수 있습니다. 기관 검토에 필요한 소개 범위는 문의 시 알려 주세요.')]
    body += '<div class="s-faq">' + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs) + '</div></div></section>'
    page('contact.html', '교육·강연·기업 멘토링 문의', 'SotoLAB 장성균 박사의 맞춤 교육·강연·기업 AI 멘토링·대학 연계 AIoT 교육 문의 · 기관과 대상, 목표에 맞는 교육을 함께 준비합니다.', body)


def build_education_cases():
    body = '<section class="s-page-head"><div class="s-wrap"><p class="s-eyebrow">TEACHING IN PRACTICE</p><h1>교육의 현장과,<br>배움으로 남긴 기록</h1><p>강의확인서와 대학 공식 기사, 교육 교재로 살펴보는 교육 사례입니다. 대상에 맞게 구성한 수업과 실제로 다룬 내용을 소개합니다.</p></div></section><section class="s-section" style="padding-top:10px"><div class="s-wrap"><div class="s-grid-3">'
    for i in (1, 4, 11):
        row = ROWS[i]
        body += f'<article class="s-card"><span class="s-card-number">{escape(row["period"])}</span><h2 style="font-size:24px">{escape(row["title"])}</h2><p>{escape(row["organization"])}</p><p>{escape(row["result"])}</p><p class="s-outcome">{escape(row["lesson"])}</p><p class="s-small">근거: {escape(row["source"])}</p></article>'
    body += '</div><div class="s-actions"><a class="s-button" href="experience.html?category=education#archive-results">전체 교육 이력 보기 →</a><a class="s-button" href="https://www.catholic.ac.kr/ko/newsroom/photonews.do?mode=view&amp;articleNo=274897" target="_blank" rel="noopener noreferrer">대학 공식 기사 보기 ↗</a></div></div></section>'
    page('reviews.html', '교육 사례와 활동 기록', '강의확인서와 대학 공식 기사, 교육 교재로 살펴보는 SotoLAB 장성균 박사의 교육·강의 사례', body + cta())


def build_service_pages():
    page('academy.html', '교육·강연 아카데미',
         'AI·AIoT, 임베디드, 블록체인 실습교육과 맞춤 강연을 장성균 박사의 실무·연구 경험으로 연결합니다.',
         (ROOT / 'data/academy-content.html').read_text(encoding='utf-8'))
    page('sotolab.html', '기업 AI 멘토링 · 업무 도구 구축',
         '개인에서 팀으로, 팀에서 조직으로 연결하는 SotoLAB 기업 AI 멘토링 · 업무 적용과 내부 업무 도구 제작을 함께합니다.',
         (ROOT / 'data/mentoring-content.html').read_text(encoding='utf-8'))


def update_detail_navigation():
    """Share the complete menu with existing detail pages without changing their content."""
    names = ['academy-interior.html', 'academy-practice.html', 'academy-special.html',
             'academy-visit.html', 'academy-business.html', 'curriculum.html',
             'online.html', 'mvp-projects.html']
    assets = f'''<!-- SOTOLAB_NAV_ASSETS --><link rel="stylesheet" href="css/sotolab-brand.css?v={BRAND_ASSET_VERSION}"><script src="js/sotolab-brand.js?v={BRAND_ASSET_VERSION}" defer></script><script src="js/sotolab-space.js?v={BRAND_ASSET_VERSION}" defer></script><script src="js/sotolab-scroll.js?v={BRAND_ASSET_VERSION}" defer></script><noscript><style>.s-menu{{display:flex!important}}.s-menu-toggle{{display:none!important}}</style></noscript><!-- /SOTOLAB_NAV_ASSETS -->'''
    for name in names:
        path = ROOT / name
        html = path.read_text(encoding='utf-8-sig')
        # Shared scroll controls replace the original page-specific top button.
        html = re.sub(r'<button\b[^>]*\bid="scrollTop"[^>]*>.*?</button>', '', html, flags=re.S)
        html = re.sub(r'<canvas\b[^>]*\bid="webgl"[^>]*></canvas>', '', html)
        html = re.sub(r'<div class="(?:shade|grid)"></div>', '', html)
        parent = 'academy.html' if name.startswith('academy-') else 'sotolab.html'
        shared = nav(parent)
        if '<!-- SOTOLAB_NAV_START -->' in html:
            html = re.sub(r'<!-- SOTOLAB_NAV_START -->.*?<!-- SOTOLAB_NAV_END -->', lambda _: shared, html, count=1, flags=re.S)
        elif '<header class="header">' in html:
            html = re.sub(r'<a class="skip" href="#main">.*?</a>', '', html, count=1, flags=re.S)
            html = re.sub(r'<header class="header">.*?</header>', lambda _: shared, html, count=1, flags=re.S)
        elif '<nav class="nav">' in html:
            html = re.sub(r'<nav class="nav">.*?</nav>', lambda _: shared, html, count=1, flags=re.S)
        else:
            raise ValueError(f'Cannot locate navigation in {name}')
        if '<!-- SOTOLAB_NAV_ASSETS -->' in html:
            html = re.sub(r'<!-- SOTOLAB_NAV_ASSETS -->.*?<!-- /SOTOLAB_NAV_ASSETS -->', lambda _: assets, html, count=1, flags=re.S)
        else:
            html = html.replace('</head>', assets + '</head>', 1)
        if 'class="s-legacy-page"' not in html:
            html = html.replace('<body>', '<body class="s-legacy-page">', 1)
        if 'id="main"' not in html:
            html, count = re.subn(r'(<section\b[^>]*\bclass="page-header")', r'\1 id="main"', html, count=1)
            if not count:
                raise ValueError(f'Cannot locate main content in {name}')
        if name == 'academy-interior.html':
            html = re.sub(r'js/academy-interior.js\?v=[^"\s]+', f'js/academy-interior.js?v={BRAND_ASSET_VERSION}', html)
        html = re.sub(r'(?m)^[ \t]+$', '', html)
        path.write_text(html, encoding='utf-8')


if __name__ == '__main__':
    build_home()
    build_profile()
    build_experience()
    build_books()
    build_contact()
    build_education_cases()
    build_service_pages()
    update_detail_navigation()
    print(f'Built eight brand pages and eight detail menus with {len(ROWS)} activity records.')

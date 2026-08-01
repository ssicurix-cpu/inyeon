"""
webapp.seo — SEO 콘텐츠 페이지 (복리 검색 유입).

각 페이지는 특정 검색어를 타겟. 깨끗한 URL + 메타태그 + 내부링크 + 무료도구 CTA.
슬러그 → 콘텐츠 dict. _render(slug)로 공유 템플릿에 렌더.
"""
from __future__ import annotations

BASE = "https://inyeon.onrender.com"

_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{base}/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{base}/{slug}">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-6QNQRMT8FH"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-6QNQRMT8FH');</script>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0a0b1a;--card:#161936;--line:#2a2d55;--text:#f1f0fb;--muted:#a9a8cc;--dim:#6f6e93;--gold:#e8c86c;--jade:#8fe0bd}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;line-height:1.65}}
.wrap{{max-width:760px;margin:0 auto;padding:34px 20px 70px}}
.brand{{font-family:'Cormorant Garamond',serif;font-size:22px;letter-spacing:.06em;text-align:center;margin-bottom:2px}}
.brand a{{color:var(--text);text-decoration:none}}
h1{{font-family:'Cormorant Garamond',serif;font-size:36px;font-weight:700;line-height:1.15;margin:22px 0 10px}}
h2{{font-family:'Cormorant Garamond',serif;font-size:26px;font-weight:600;margin:36px 0 8px;color:var(--gold)}}
p{{color:#e4e3f5;margin:12px 0}}
.lede{{font-size:19px;color:var(--muted)}}
a{{color:var(--jade)}}
a.cta{{display:inline-block;background:var(--gold);color:#231b03;font-weight:600;padding:14px 26px;border-radius:40px;text-decoration:none;margin:22px 0}}
.elrow{{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}}
.elchip{{border:1px solid var(--line);border-radius:30px;padding:7px 15px;font-size:14px;color:var(--muted)}}
.more{{margin-top:44px;border-top:1px solid var(--line);padding-top:18px}}
.more a{{display:block;color:var(--gold);text-decoration:none;padding:7px 0;font-size:15px}}
.foot{{margin-top:34px;border-top:1px solid var(--line);padding-top:18px;color:var(--dim);font-size:13px;text-align:center}}
.faq b{{color:var(--text)}}
</style></head>
<body><div class="wrap">
<div class="brand"><a href="/">☾ Inyeon</a></div>
"""

_RELATED = {
    "what-is-saju": "What is Saju? (Korean Four Pillars)",
    "missing-element": "What is your Missing Element?",
    "saju-compatibility": "How Korean Saju compatibility works",
    "korean-name": "Get a Korean name from your birthday",
}


def _related_block(current: str) -> str:
    links = [f'<a href="/{s}">{t} →</a>' for s, t in _RELATED.items() if s != current]
    links.append('<a href="/learn">The full guide to Korean saju →</a>')
    return '<div class="more"><h2>Keep reading</h2>' + "".join(links) + "</div>"


PAGES = {
    "what-is-saju": {
        "title": "What Is Saju? Korean Four Pillars of Destiny, Explained — Inyeon",
        "desc": "Saju (사주) is Korean four pillars of destiny — it reads your exact birth date, time and place as eight characters and five elements. Learn what saju is and get your free chart.",
        "body": """
<h1>What Is Saju? Korean Four Pillars of Destiny, Explained</h1>
<p class="lede">Saju (사주, "four pillars of destiny") is a Korean and East-Asian system that reads you from your exact birth <em>year, month, day and hour</em> — not just your month like a Western sun sign.</p>
<a class="cta" href="/start">Get your free saju chart →</a>

<h2>The eight characters (八字)</h2>
<p>Each of your four "pillars" — year, month, day and hour — is written with two characters: one heavenly stem and one earthly branch. Together that's <b>eight characters</b> (八字, sometimes romanized "BaZi"). These characters are drawn from the sexagenary cycle and the 24 solar terms of the lunisolar calendar, so saju is a <b>calendar-based</b> reading, not a star reading.</p>

<h2>The five elements (오행)</h2>
<p>Every character maps onto one of five elements — Wood, Fire, Earth, Metal and Water. Your chart usually leans heavy on some and light on others.</p>
<div class="elrow"><span class="elchip">🌳 Wood</span><span class="elchip">🔥 Fire</span><span class="elchip">🪨 Earth</span><span class="elchip">⚪ Metal</span><span class="elchip">💧 Water</span></div>
<p>Your "day master" — the stem of your day pillar — is treated as <em>you</em>, and the rest of the chart is read in relation to it.</p>

<h2>How is saju different from Western astrology?</h2>
<p>Western sun-sign astrology gives everyone born in the same month one label. Saju uses your precise birth moment (with true-solar-time and timezone corrections) to build eight characters, so it's far more specific than "you're a Gemini." It's less about fixed fate and more about the balance of energies in you — which you lean on, and which you're <a href="/missing-element">missing</a>.</p>

<h2>Is saju fortune telling?</h2>
<p>At Inyeon we treat saju as a lens for <b>self-discovery and entertainment</b>, not fixed fate. The most useful part isn't prediction — it's seeing your <a href="/missing-element">missing element</a>, the energy you can grow into.</p>

<a class="cta" href="/start">Draw my free chart + find my missing element →</a>
""",
    },
    "missing-element": {
        "title": "What Is Your Missing Element in Saju? Find Yours Free — Inyeon",
        "desc": "Your missing element is the one of the five elements (wood, fire, earth, metal, water) your saju chart lacks — and it tends to be your growth edge. Find yours free.",
        "body": """
<h1>What Is Your "Missing Element" in Saju?</h1>
<p class="lede">Anyone can describe your elements. The more useful question is the one Inyeon asks: which of the five elements are you <b>missing</b>? That lack tends to be your growth edge — the energy you keep reaching for.</p>
<a class="cta" href="/start">Find my missing element →</a>

<h2>The five elements, and the one you lack</h2>
<p>Saju maps your <a href="/what-is-saju">eight birth characters</a> onto five elements: Wood, Fire, Earth, Metal and Water. Most charts are heavy in a few and thin — or empty — in one. That thin one is your missing element.</p>
<div class="elrow"><span class="elchip">🌳 Wood — growth, vision</span><span class="elchip">🔥 Fire — passion, warmth</span><span class="elchip">🪨 Earth — stability, care</span><span class="elchip">⚪ Metal — structure, clarity</span><span class="elchip">💧 Water — depth, wisdom</span></div>

<h2>Why the element you lack matters most</h2>
<p>In traditional saju, the balancing element (용신) — often the one you're short on — is what a chart "wants" more of. We frame it simply: <b>the element you're missing is the one to grow into.</b> No water? You may crave calm, depth, people who feel like still lakes. No fire? You're drawn to warmth and drive.</p>

<h2>What you can do with it</h2>
<p>Your missing element is the through-line of everything at Inyeon: a <a href="/korean-name">Korean name</a> built to fill it, and <a href="/saju-compatibility">compatibility</a> you can tune — where you and another person each carry the element the other is missing.</p>

<a class="cta" href="/start">Reveal my missing element (free) →</a>
""",
    },
    "saju-compatibility": {
        "title": "Korean Saju Compatibility — How Two Charts Fit — Inyeon",
        "desc": "Korean saju compatibility is birthdate-based and gender-neutral — it works for partners, friends, family, even pets. See how two charts' elements flow, and get your couple name.",
        "body": """
<h1>Korean Saju Compatibility — How Two Charts Fit</h1>
<p class="lede">Saju compatibility isn't "you're both fire signs so you clash." It reads how two people's <a href="/what-is-saju">five elements</a> flow between each other — where you feed one another, and where you spark.</p>
<a class="cta" href="/start">Check your compatibility free →</a>

<h2>Gender-neutral, any relationship</h2>
<p>Because the calculation uses birth dates — not gender roles — saju compatibility works for romantic partners, friends, family, coworkers, even your dog or cat. There's no "husband star / wife star" here: just how two charts' energies meet.</p>

<h2>How elements flow (생 and 극)</h2>
<p>Elements relate through generation (생, one nourishes the next) and control (극, one checks another). Compatibility looks at how your day masters and elements interact — feeding cycles read as ease, controlling cycles read as tension and attraction. Tension isn't "bad": we frame it as growth and pull, not a verdict.</p>

<h2>The couple-name layer</h2>
<p>On top of the birth reading, Inyeon adds a name layer. We build a <a href="/korean-name">Korean name pair</a> where <b>each name carries the element the other person is missing</b> — so you become each other's missing piece. Your day master and zodiac are fixed at birth and can't change; what a name tunes is the harmony layer, for fun and self-discovery.</p>

<a class="cta" href="/start">See your saju compatibility + couple name →</a>
""",
    },
    "korean-name": {
        "title": "Get a Korean Name From Your Birthday (Not a Translator) — Inyeon",
        "desc": "A real Korean name built from your saju — it fills the element your chart is missing, with real hanja, meaning and sound. Not a translator swap. Get yours free.",
        "body": """
<h1>Get a Korean Name From Your Birthday</h1>
<p class="lede">Not the "type your name into a translator" kind — those are just sound-swaps. A real Korean name can be built from your <a href="/what-is-saju">saju</a>, to fill the element your chart is <a href="/missing-element">missing</a>.</p>
<a class="cta" href="/name">Reveal my Korean name →</a>

<h2>How saju-based naming works</h2>
<p>Korean naming traditionally balances a chart through the name's energy, on two channels: <b>발음오행</b> (the element of the name's <em>sound</em>, from its initial consonants) and <b>자원오행</b> (the element carried by the <em>hanja</em> characters themselves). If your chart is missing water, a name can pour water in — in how it sounds and what its characters mean.</p>

<h2>Real hanja, real meaning</h2>
<p>Each name comes with its hanja (Chinese characters used in Korean), the meaning of each character, and its element — so it's a name with substance, chosen from a pool of natural, modern Korean names rather than invented on the spot. It's inspired by your own name, but made for your chart.</p>

<h2>Honest framing</h2>
<p>This is for self-discovery and fun, crafted the traditional 오행 way — not a claim to change your fate. It's less "translate me" and more "a name that fits me." For couples, we can even make a <a href="/saju-compatibility">pair of names</a> where each fills the other's missing element.</p>

<a class="cta" href="/name">Get my Korean name (free) →</a>
""",
    },
}


def render(slug: str) -> str | None:
    page = PAGES.get(slug)
    if not page:
        return None
    head = _HEAD.format(title=page["title"], desc=page["desc"], base=BASE, slug=slug)
    foot = _related_block(slug) + (
        '<div class="foot">For entertainment &amp; self-discovery. '
        'Inyeon — Korean saju &amp; compatibility for the world · '
        '<a href="/">inyeon.onrender.com</a></div></div></body></html>'
    )
    return head + page["body"] + foot


def sitemap() -> str:
    urls = ["", "start", "name", "learn", "signup"] + list(PAGES.keys())
    items = "".join(f"<url><loc>{BASE}/{u}</loc></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + items + "</urlset>")


def robots() -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n"

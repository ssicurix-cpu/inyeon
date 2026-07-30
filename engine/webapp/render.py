"""
webapp.render — 리딩 → 브랜드 스타일 결과 HTML (자기완결, 인라인 CSS).
랜딩과 같은 딥 잉크 + 금빛 무드.
"""
from __future__ import annotations

import json

from saju.core import Element
from saju.interpret import NATURE

_ELEM_COLOR = {
    Element.WOOD: "#8fe0bd", Element.FIRE: "#f0a6a6", Element.EARTH: "#e8c86c",
    Element.METAL: "#cfd2ee", Element.WATER: "#7fa8e6",
}

_POLARITY_DESC = {"Yang": "bold, outward and active", "Yin": "soft, inward and reflective"}

_PAGE_HEAD = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Your Inyeon reading</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--ink:#0a0b1a;--panel:#161936;--panel2:#1d2044;--line:#2a2d55;--gold:#e8c86c;--jade:#8fe0bd;--text:#f1f0fb;--muted:#a9a8cc;--dim:#7a7aa0}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--ink);color:var(--text);font-family:'Inter',system-ui,sans-serif;line-height:1.6;padding:26px 16px}
.card{max-width:520px;margin:0 auto;background:linear-gradient(160deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:24px;padding:30px 26px;box-shadow:0 30px 80px rgba(0,0,0,.4)}
.serif{font-family:'Cormorant Garamond',serif}
.eyebrow{color:var(--gold);font-size:12px;letter-spacing:.18em;text-transform:uppercase}
h1{font-family:'Cormorant Garamond',serif;font-size:32px;font-weight:600;line-height:1.15;margin:6px 0 4px}
.kind{color:var(--muted);font-size:14px}
.pillars{display:flex;gap:9px;justify-content:center;font-family:'Cormorant Garamond',serif;font-size:28px;margin:22px 0 6px}
.pillars .dm{color:var(--gold)}
.plabels{display:flex;gap:9px;justify-content:center;color:var(--dim);font-size:11px;margin-bottom:14px}
.plabels span{flex:1;text-align:center}
.bars{display:flex;align-items:flex-end;gap:11px;height:92px;margin:12px 0}
.bars .b{flex:1;display:flex;flex-direction:column;align-items:center;gap:7px}
.bars .bar{width:100%;border-radius:5px 5px 0 0}
.bars small{font-size:11px;color:var(--dim)}
.missing{background:rgba(143,224,189,.1);border:1px solid rgba(143,224,189,.4);border-radius:14px;padding:14px 16px;margin:14px 0}
.missing b{color:var(--jade)}
.reading{font-family:'Cormorant Garamond',serif;font-size:19px;font-style:italic;line-height:1.55;color:#e9e8fb;margin:16px 0}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.chip{font-size:12px;border:1px solid var(--line);border-radius:30px;padding:5px 13px;color:var(--muted)}
.badge{display:inline-block;font-size:12px;color:var(--gold);border:1px solid var(--gold);border-radius:30px;padding:4px 12px;margin-bottom:14px}
.hint{font-size:12px;color:var(--dim);line-height:1.55;margin-top:8px}
.hint b{color:var(--muted);font-weight:500}
.compat{margin-top:26px;border-top:1px solid var(--line);padding-top:22px}
.score{font-family:'Cormorant Garamond',serif;font-size:44px;color:var(--gold);font-weight:600}
.ladder{margin:14px 0;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.lrow{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}
.lrow:first-child{border-top:none}
.lrow b{color:var(--text);font-size:15px}
.lrow.hot{background:rgba(232,200,108,.1)}
.lrow.hot b{color:var(--gold)}
.sendcta{display:block;text-align:center;border:1px solid var(--gold);color:var(--gold);font-weight:600;padding:13px;border-radius:40px;margin-top:12px;text-decoration:none;font-size:14px}
.cta{display:block;text-align:center;background:var(--gold);color:#231b03;font-weight:600;padding:14px;border-radius:40px;margin-top:22px;text-decoration:none}
.sec{margin-top:24px}
.askbox{display:flex;gap:8px;margin-top:8px}
.askbox input{flex:1;padding:11px;background:#0f1124;border:1px solid var(--line);border-radius:10px;color:var(--text);font-size:14px}
.askbox button{background:var(--gold);color:#231b03;border:none;border-radius:10px;padding:0 16px;font-weight:600;cursor:pointer}
.foot{max-width:520px;margin:16px auto 0;text-align:center;color:var(--dim);font-size:11px}
</style></head><body>"""

_PAGE_FOOT = """<p class="foot">For entertainment & self-discovery. Inyeon — Korean saju & compatibility.</p></body></html>"""


def _bars(counts: dict[Element, int]) -> str:
    mx = max(max(counts.values()), 1)
    order = [Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER]
    out = []
    for e in order:
        n = counts[e]
        if n == 0:
            bar = f'<div class="bar" style="height:6px;border:1px dashed {_ELEM_COLOR[e]}"></div>'
        else:
            h = int(18 + (72 * n / mx))
            bar = f'<div class="bar" style="height:{h}px;background:{_ELEM_COLOR[e]}"></div>'
        out.append(f'<div class="b">{bar}<small>{e.en}</small></div>')
    return '<div class="bars">' + "".join(out) + "</div>"


def render_result(data: dict) -> str:
    c = data["chart"]
    dm = c.day_master
    nature, traits = NATURE[dm.hanja]
    p = c.pillars
    persona = data["persona"]

    who = data.get("name")
    title = f"{who}'s reading" if who else "Your reading"

    html = [_PAGE_HEAD, '<div class="card">']
    html.append(f'<div class="badge">{persona.label_en}</div>')
    html.append(f'<div class="eyebrow">{title} · your day master</div>')
    html.append(f'<h1>{dm.polarity.en} {dm.element.en}<br><span style="font-size:22px;color:var(--muted)">{nature}</span></h1>')
    html.append(f'<div class="hint">Your <b>Day Master</b> is the core "you" in Korean saju — '
                f'the sign of the exact day you were born. <b>{dm.polarity.en}</b> means '
                f'{_POLARITY_DESC[dm.polarity.en]}, and your element is <b>{dm.element.en}</b> — '
                f'so, {dm.polarity.en} {dm.element.en}.</div>')
    html.append('<div class="pillars">'
                + f'<span>{p["year"]}</span><span>{p["month"]}</span>'
                + f'<span class="dm">{p["day"]}</span><span>{p["hour"]}</span></div>')
    html.append('<div class="plabels"><span>year</span><span>month</span><span>day</span><span>hour</span></div>')
    html.append('<div class="hint">Your <b>Four Pillars</b> — eight Korean signs drawn from your '
                'birth year, month, day and hour. The day sign (gold) is your Day Master.</div>')
    html.append(_bars(c.element_counts))
    html.append('<div class="hint">The five elements you\'re made of. The one you lack is your growth edge.</div>')
    if c.lacking:
        miss = c.lacking[0]
        html.append(f'<div class="missing">Your missing element: <b>{miss.en}</b> — your growth edge.</div>')
    html.append(f'<div class="reading">{data["reading"]}</div>')
    html.append('<div class="chips">'
                + f'<span class="chip">☾ lunar {c.lunar.year}-{c.lunar.month:02d}-{c.lunar.day:02d}</span>'
                + f'<span class="chip">{c.zodiac.animal_en} zodiac</span></div>')
    d = data.get("daily")
    if d:
        html.append('<div class="sec"><div class="eyebrow">Today\'s energy · ' + d["ganzhi"]
                    + '</div><div class="hint" style="font-size:14px">' + d["text"] + '</div></div>')
    rt = data.get("ritual")
    if rt:
        acts = " · ".join(rt["activities"])
        html.append('<div class="sec"><div class="eyebrow">Your ritual — cultivate '
                    + rt["element_en"] + '</div><div class="missing" style="background:rgba(232,200,108,.08);border-color:rgba(232,200,108,.3)">'
                    + f'<b style="color:var(--gold)">{rt["practice"]}</b>'
                    + f'<div class="hint" style="margin-top:6px">Color {rt["color"]} · {rt["direction"]} · {rt["time"]} — {acts}.</div></div></div>')

    if "compat" in data:
        comp = data["compat"]
        pname = data.get("partner_name")
        clabel = f"Your compatibility with {pname}" if pname else "Your compatibility"
        html.append('<div class="compat">')
        html.append(f'<div class="eyebrow">{clabel}</div>')
        html.append(f'<div class="score">{comp.score}%</div>')
        html.append(f'<div class="hint" style="margin-top:-2px;color:var(--gold)">{comp.tier}</div>')
        html.append(f'<div class="reading" style="font-size:17px">{data["compat_text"]}</div>')
        rec = data.get("name_rec")
        pname = data.get("partner_name") or "them"
        if rec and rec.get("best"):
            html.append(f'<div class="missing">Your Korean name <b>{rec["best"].hangul}</b> '
                        f'(adds {rec["harmonizing_element"].en}) tunes the harmony between you.</div>')
            html.append('<div class="ladder">'
                        f'<div class="lrow"><span>Right now</span><b>{rec["base_score"]}%</b></div>'
                        f'<div class="lrow"><span>+ your Korean name</span><b>{rec["boosted_score"]}%</b></div>'
                        f'<div class="lrow hot"><span>+ {pname}\'s Korean name too</span>'
                        f'<b>{rec["both_boosted"]}% · {rec["both_tier"]}</b></div></div>')
            html.append(f'<a class="sendcta" href="#">Send this to {pname} → reach '
                        f'{rec["both_boosted"]}% together</a>')
        html.append('</div>')

    inp = data.get("inputs") or {}
    html.append('<div class="sec"><div class="eyebrow">Ask ' + persona.label_en + '</div>'
                '<div class="askbox"><input id="q" placeholder="Ask about love, career, timing…"/>'
                '<button id="qbtn" type="button">Ask</button></div>'
                '<div id="ans" class="reading" style="font-size:16px;display:none;margin-top:10px"></div></div>')
    html.append('<script>const I=' + json.dumps(inp) + ';'
                'document.getElementById("qbtn").onclick=async()=>{'
                'const q=document.getElementById("q").value.trim();if(!q)return;'
                'const a=document.getElementById("ans");a.style.display="block";a.textContent="…";'
                'const f=new URLSearchParams(Object.assign({},I,{question:q}));'
                'const res=await fetch("/ask",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:f});'
                'const j=await res.json();a.textContent=j.text;};</script>')
    html.append('<a class="cta" href="#">Get your Korean destiny name</a>')
    html.append('</div>')
    html.append(_PAGE_FOOT)
    return "".join(html)


# ── 9:16 공유 카드 (바이럴 엔진) ─────────────────────────────────────────────
_CARD_HEAD = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Inyeon share card</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#050612;display:flex;justify-content:center;padding:16px;font-family:'Inter',sans-serif}
.card9{position:relative;width:min(410px,94vw);aspect-ratio:9/16;background:#0a0b1a;border:1px solid #33366b;border-radius:26px;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;padding:40px 30px;color:#f4f3fc;text-align:center;box-shadow:0 40px 90px rgba(0,0,0,.55),inset 0 0 70px rgba(0,0,0,.55)}
.bgimg{position:absolute;inset:0;background:url('https://d8j0ntlcm91z4.cloudfront.net/user_3GGa0mUII1gOCwgWZmnTJH6OoHX/hf_20260730_135939_5e04c0ff-68dc-4519-829d-14a833e49413.png') center/cover no-repeat;opacity:.62}
.veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,6,18,.82) 0%,rgba(5,6,18,.4) 42%,rgba(5,6,18,.72) 72%,rgba(5,6,18,.95) 100%)}
.glowtop{position:absolute;top:-18%;left:-10%;width:120%;height:52%;background:radial-gradient(circle,rgba(232,200,108,.2),transparent 70%);pointer-events:none}
.brand{position:relative;z-index:2;font-family:'Cormorant Garamond',serif;font-size:25px;letter-spacing:.06em;color:#f4f3fc}
.brand b{color:#e8c86c}
.mid{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center;gap:13px;margin:auto 0}
.eyebrow{color:#f0d488;font-size:13px;letter-spacing:.24em;text-transform:uppercase;font-weight:600}
.names{font-family:'Cormorant Garamond',serif;font-size:37px;font-weight:600}
.bigscore{font-family:'Cormorant Garamond',serif;font-size:104px;font-weight:600;color:#e8c86c;line-height:1;text-shadow:0 6px 34px rgba(232,200,108,.4)}
.tier{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:28px;color:#f4f3fc}
.flow{color:#d0cfeb;font-size:18px;max-width:310px;line-height:1.5}
.bigelem{font-family:'Cormorant Garamond',serif;font-size:88px;font-weight:600;line-height:1.05;text-shadow:0 6px 34px rgba(0,0,0,.55)}
.nature{color:#d0cfeb;font-size:21px}
.mbars{display:flex;align-items:flex-end;gap:12px;height:74px;margin-top:10px}
.mbars i{width:26px;border-radius:4px 4px 0 0;display:block}
.tease{margin-top:12px;border:1px solid rgba(232,200,108,.55);background:rgba(232,200,108,.14);border-radius:16px;padding:14px 17px;font-size:16px;color:#f0d488;max-width:310px;font-weight:500;line-height:1.45}
.line{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:24px;color:#f4f3fc;max-width:300px;line-height:1.4}
.wm{position:relative;z-index:2;color:#bcbbda;font-size:15px;letter-spacing:.04em}
.wm b{color:#e8c86c}
</style></head><body>"""


def _mini_bars(counts: dict[Element, int]) -> str:
    mx = max(max(counts.values()), 1)
    order = [Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER]
    out = []
    for e in order:
        n = counts[e]
        if n == 0:
            out.append(f'<i style="height:8px;border:1px dashed {_ELEM_COLOR[e]}"></i>')
        else:
            out.append(f'<i style="height:{int(12 + 46 * n / mx)}px;background:{_ELEM_COLOR[e]}"></i>')
    return '<div class="mbars">' + "".join(out) + "</div>"


def render_card(data: dict) -> str:
    """9:16 공유 카드. 궁합이 있으면 커플 카드, 없으면 Missing Element 카드."""
    c = data["chart"]
    who = data.get("name") or "You"
    h = [_CARD_HEAD, '<div class="card9">',
         '<div class="bgimg"></div><div class="veil"></div><div class="glowtop"></div>',
         '<div class="brand">☾ <b>Inyeon</b></div>']

    if "compat" in data:
        comp = data["compat"]
        pname = data.get("partner_name") or "them"
        dm_txt = comp.day_master["en"].split(" — ")[0]
        rec = data.get("name_rec")
        h.append('<div class="mid">')
        h.append('<div class="eyebrow">Korean saju compatibility</div>')
        h.append(f'<div class="names">{who} × {pname}</div>')
        h.append(f'<div class="bigscore">{comp.score}%</div>')
        h.append(f'<div class="tier">{comp.tier}</div>')
        h.append(f'<div class="flow">{dm_txt}.</div>')
        if rec and rec.get("best"):
            h.append(f'<div class="tease">Both get your Korean names to unlock '
                     f'〈{rec["both_tier"]}〉 — find out how high ✨</div>')
        h.append('</div>')
        h.append(f'<div class="wm">what\'s your inyeon? · <b>inyeon.app</b></div>')
    else:
        miss = c.lacking[0] if c.lacking else c.dominant
        h.append('<div class="mid">')
        h.append(f'<div class="eyebrow">{who}\'s missing element</div>')
        h.append(f'<div class="bigelem" style="color:{_ELEM_COLOR[miss]}">{miss.en}</div>')
        h.append(f'<div class="nature">{c.day_master.polarity.en} {c.day_master.element.en} · '
                 f'{NATURE[c.day_master.hanja][0]}</div>')
        h.append(_mini_bars(c.element_counts))
        h.append('<div class="line">The one energy I\'m missing — my growth edge.</div>')
        h.append('</div>')
        h.append(f'<div class="wm">what\'s yours? · <b>inyeon.app</b></div>')

    h.append('</div></body></html>')
    return "".join(h)

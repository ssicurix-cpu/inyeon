"""
webapp.app — FastAPI 웹앱: 입력 폼 → 실제 엔진 계산 → 결과 페이지.
로컬 실행: uvicorn webapp.app:app --reload
배포: Cloud Run 등 서버리스(0으로 축소).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

from saju.place import CITIES, chart_for_place
from .reading import build_reading
from .render import render_result
from saju.place import chart_for_city
from saju.ask import ask as _ask
from .reading import PERSONA_MAP

app = FastAPI(title="Inyeon — Korean Saju")

_CITY_OPTS = "".join(f'<option>{c}</option>' for c in CITIES)
_CITIES_DATA = json.loads((Path(__file__).parent / "static" / "cities.json").read_text(encoding="utf-8"))


@app.get("/api/cities")
def api_cities(q: str = ""):
    """City search for autocomplete → [{label, tz, lng}] (population-ordered)."""
    q = q.strip().lower()
    if len(q) < 2:
        return []
    starts, contains = [], []
    for c in _CITIES_DATA:
        n = c["n"].lower()
        if n.startswith(q):
            starts.append(c)
        elif q in n:
            contains.append(c)
        if len(starts) >= 12:
            break
    res = (starts + contains)[:12]
    return [{"label": f'{c["n"]}, {c["c"]}', "tz": c["tz"], "lng": c["lng"]} for c in res]


def _chart_tz(dt, tz, lng, city):
    if tz and lng not in (None, ""):
        try:
            return chart_for_place(dt, tz, float(lng))
        except Exception:
            pass
    try:
        return chart_for_city(dt, city or "Seoul")
    except Exception:
        return chart_for_city(dt, "Seoul")
_PERSONAS = [("warm", "The Warm Guide", "Warm &amp; comforting"),
             ("blunt", "The Straight Talker", "No sugar-coating"),
             ("mystic", "The Mystic", "Mysterious &amp; knowing")]


def _form_page() -> str:
    prad = "".join(
        f'<label class="rcard{" sel" if k=="warm" else ""}"><input type="radio" name="persona" value="{k}"{" checked" if k=="warm" else ""}>'
        f'<img src="/char/{k}?v=2" alt="{v}" loading="lazy"><div class="rn">{v}</div><div class="rt">{t}</div></label>'
        for k, v, t in _PERSONAS)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Inyeon — your reading</title>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-6QNQRMT8FH"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-6QNQRMT8FH');</script>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
body{{background:#0a0b1a;color:#f1f0fb;font-family:'Inter',sans-serif;padding:30px 16px}}
.card{{max-width:440px;margin:0 auto;background:#161936;border:1px solid #2a2d55;border-radius:22px;padding:28px}}
h1{{font-family:'Cormorant Garamond',serif;font-size:30px;font-weight:600;margin-bottom:4px}}
.sub{{color:#a9a8cc;font-size:14px;margin-bottom:20px}}
label{{display:block;font-size:13px;color:#a9a8cc;margin:14px 0 6px}}
input,select{{width:100%;padding:11px;background:#0f1124;border:1px solid #2a2d55;border-radius:10px;color:#f1f0fb;font-size:14px}}
.p{{display:inline-flex;align-items:center;gap:6px;margin:6px 12px 0 0;color:#f1f0fb;font-size:13px}}
.p input{{width:auto}}
.readers{{display:flex;gap:8px;margin-top:6px}}
.rcard{{flex:1;cursor:pointer;background:#0f1124;border:2px solid #2a2d55;border-radius:12px;padding:6px;text-align:center;transition:border-color .2s}}
.rcard img{{width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:8px;display:block}}
.rcard .rn{{font-size:11px;color:#f1f0fb;margin-top:5px;font-weight:600;line-height:1.2}}
.rcard .rt{{font-size:9px;color:#a9a8cc;margin-top:2px}}
.rcard input{{display:none}}
.rcard:has(input:checked){{border-color:#e8c86c;box-shadow:0 0 0 1px #e8c86c}}
.rcard.sel{{border-color:#e8c86c;box-shadow:0 0 0 1px #e8c86c}}
.row{{display:flex;gap:10px}} .row>div{{flex:1}}
button{{width:100%;background:#e8c86c;color:#231b03;font-weight:600;border:none;padding:14px;border-radius:40px;margin-top:22px;font-size:15px;cursor:pointer}}
details{{margin-top:20px}}
summary{{list-style:none;color:#e8c86c;font-size:15px;font-weight:600;cursor:pointer;border:1px solid #e8c86c;border-radius:12px;padding:15px;text-align:center;background:rgba(232,200,108,.09);transition:background .2s}}
summary::-webkit-details-marker{{display:none}}
summary:hover{{background:rgba(232,200,108,.18)}}
details[open] summary{{margin-bottom:8px}}
.topbar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}}
.brandlink{{font-family:'Cormorant Garamond',serif;font-size:20px;color:#f1f0fb;text-decoration:none;letter-spacing:.04em}}
.closex{{color:#a9a8cc;text-decoration:none;font-size:26px;line-height:1;padding:0 8px;border-radius:8px}}
.closex:hover{{background:#0f1124;color:#f1f0fb}}
.acwrap{{position:relative}}
.ac{{position:absolute;left:0;right:0;top:100%;z-index:30;background:#0f1124;border:1px solid #2a2d55;border-top:none;border-radius:0 0 10px 10px;max-height:210px;overflow:auto;display:none}}
.ac div{{padding:10px 12px;font-size:14px;color:#f1f0fb;cursor:pointer;border-top:1px solid #1c1f3d}}
.ac div:hover{{background:#1a1d3d}}
</style></head><body>
<form class="card" method="post" action="/reading">
  <div class="topbar"><a href="/" class="brandlink">☾ Inyeon</a><a href="/" class="closex" title="Back to home">×</a></div>
  <h1>Discover your <em>Inyeon</em></h1>
  <div class="sub">Korean saju & compatibility · your missing element</div>
  <label>Your first name (optional)</label><input name="name" placeholder="Emma">
  <div class="row"><div><label>Birth date</label><input type="date" name="date" value="1990-06-21" required></div>
  <div><label>Time</label><input type="time" name="time" value="14:30" required></div></div>
  <label>Birth city</label>
  <div class="acwrap"><input id="city" name="city" value="Seoul, South Korea" placeholder="Type your city…" autocomplete="off"><div id="cityAC" class="ac"></div></div>
  <input type="hidden" name="tz" id="tz" value="Asia/Seoul"><input type="hidden" name="lng" id="lng" value="126.978">
  <label>Gender (for name)</label><select name="gender"><option value="F">Female</option><option value="M">Male</option></select>
  <label>Choose your reader</label><div class="readers">{prad}</div>
  <details><summary>💞 Add someone — check your compatibility</summary>
    <div class="row"><div><label>Their birth date</label><input type="date" name="p_date"></div>
    <div><label>Time</label><input type="time" name="p_time"></div></div>
    <label>Their city</label>
    <div class="acwrap"><input id="p_city" name="p_city" placeholder="Type their city…" autocomplete="off"><div id="p_cityAC" class="ac"></div></div>
    <input type="hidden" name="p_tz" id="p_tz"><input type="hidden" name="p_lng" id="p_lng">
    <div class="row"><div><label>Their name (optional)</label><input name="p_name" placeholder="Jihoon"></div>
    <div><label>Their gender (for name)</label><select name="p_gender"><option value="M">Male</option><option value="F">Female</option></select></div></div>
  </details>
  <button type="submit">Reveal my reading</button>
</form>
<script>
document.querySelectorAll('.readers .rcard').forEach(function(c){{
  c.addEventListener('click',function(){{
    document.querySelectorAll('.readers .rcard').forEach(function(x){{x.classList.remove('sel');}});
    c.classList.add('sel');
    var r=c.querySelector('input');if(r)r.checked=true;
  }});
}});
function attachAC(inId,acId,tzId,lngId){{
  var inp=document.getElementById(inId), ac=document.getElementById(acId), t;
  inp.addEventListener('input',function(){{
    document.getElementById(tzId).value=''; document.getElementById(lngId).value='';
    clearTimeout(t); var q=inp.value.trim();
    if(q.length<2){{ac.style.display='none';return;}}
    t=setTimeout(function(){{
      fetch('/api/cities?q='+encodeURIComponent(q)).then(function(r){{return r.json();}}).then(function(list){{
        ac.innerHTML='';
        list.forEach(function(c){{
          var d=document.createElement('div'); d.textContent=c.label;
          d.onclick=function(){{inp.value=c.label;document.getElementById(tzId).value=c.tz;document.getElementById(lngId).value=c.lng;ac.style.display='none';}};
          ac.appendChild(d);
        }});
        ac.style.display=list.length?'block':'none';
      }});
    }},200);
  }});
  document.addEventListener('click',function(e){{if(!ac.contains(e.target)&&e.target!==inp)ac.style.display='none';}});
}}
attachAC('city','cityAC','tz','lng');
attachAC('p_city','p_cityAC','p_tz','p_lng');
</script>
</body></html>"""


_LANDING = (Path(__file__).parent / "static" / "landing.html").read_text(encoding="utf-8")
_SIGNUP = (Path(__file__).parent / "static" / "signup.html").read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def home():
    return _LANDING


@app.get("/start", response_class=HTMLResponse)
def start():
    return _form_page()


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/api/lunar")
def api_lunar(date: str, time: str = "12:00", city: str = "Seoul",
              tz: str = "", lng: str = ""):
    """Lead magnet: lunar birthday + Korean zodiac from a birth date."""
    dt = datetime.strptime(f"{date} {time or '12:00'}", "%Y-%m-%d %H:%M")
    c = _chart_tz(dt, tz, lng, city)
    return {"lunar": f"{c.lunar.year}-{c.lunar.month:02d}-{c.lunar.day:02d}",
            "zodiac": c.zodiac.animal_en}


@app.get("/signup", response_class=HTMLResponse)
def signup():
    return _SIGNUP


_LEARN = (Path(__file__).parent / "static" / "learn.html").read_text(encoding="utf-8")


@app.get("/learn", response_class=HTMLResponse)
def learn():
    return _LEARN


@app.get("/promo/{n}", response_class=HTMLResponse)
def promo(n: int):
    p = Path(__file__).parent / "static" / f"promo{n}.html"
    if not p.exists():
        return HTMLResponse("not found", status_code=404)
    return p.read_text(encoding="utf-8")


_VID_BASE = "https://d8j0ntlcm91z4.cloudfront.net/user_3GGa0mUII1gOCwgWZmnTJH6OoHX/"
_VIDS = {
    "1": "hf_20260730_231609_bf324afc-b8fa-4551-a713-437c0e93ee9e.mp4",
    "2": "hf_20260730_231629_c8435483-2332-4679-8842-fa91c0fbd421.mp4",
    "3": "hf_20260730_233847_220e226c-afbf-4557-847d-5020abec711a.mp4",
    "4": "hf_20260730_233850_cef9b9b6-e362-4c91-8a50-b8ee0c6f1300.mp4",
    "5": "hf_20260730_233857_52fe5ff7-ed85-46ad-881f-c5790f77ae3a.mp4",
    "6": "hf_20260730_233900_c2b63497-2cc0-4ae7-8f75-1ab83ecad634.mp4",
}


_VID_CACHE: dict[str, bytes] = {}


def _fetch_vid(fn: str) -> bytes:
    if fn not in _VID_CACHE:
        from urllib.request import urlopen, Request
        req = Request(_VID_BASE + fn, headers={"User-Agent": "Mozilla/5.0"})
        _VID_CACHE[fn] = urlopen(req, timeout=30).read()
    return _VID_CACHE[fn]


@app.get("/vid/{n}")
def vid(n: str, request: Request):
    """Proxy the AI b-roll from CDN with HTTP Range support so browsers can play it."""
    from fastapi.responses import Response
    import re
    fn = _VIDS.get(n)
    if not fn:
        return Response(status_code=404)
    data = _fetch_vid(fn)
    total = len(data)
    rng = request.headers.get("range")
    if rng:
        m = re.match(r"bytes=(\d+)-(\d*)", rng)
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else total - 1
        end = min(end, total - 1)
        chunk = data[start:end + 1]
        return Response(content=chunk, status_code=206, media_type="video/mp4",
                        headers={"Content-Range": f"bytes {start}-{end}/{total}",
                                 "Accept-Ranges": "bytes",
                                 "Content-Length": str(len(chunk)),
                                 "Cache-Control": "public, max-age=86400"})
    return Response(content=data, media_type="video/mp4",
                    headers={"Accept-Ranges": "bytes", "Content-Length": str(total),
                             "Cache-Control": "public, max-age=86400"})


_CHARS = {
    "warm": "hf_20260731_115652_1e947388-3042-453e-929e-6435f254815d.png",
    "blunt": "hf_20260731_115901_39057659-4ffb-4ccb-9d6f-f5d0cb0ad17c.png",
    "mystic": "hf_20260731_115659_f13ce3f0-9c71-4891-b976-7133c56f2a08.png",
}


@app.get("/char/{key}")
def char(key: str):
    """Serve persona character art (proxied + cached from CDN)."""
    from fastapi.responses import Response
    fn = _CHARS.get(key)
    if not fn:
        return Response(status_code=404)
    data = _fetch_vid(fn)
    return Response(content=data, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=604800"})


@app.post("/reading", response_class=HTMLResponse)
def reading(date: str = Form(...), time: str = Form(...), city: str = Form(""),
            gender: str = Form("F"), persona: str = Form("warm"), name: str = Form(""),
            tz: str = Form(""), lng: str = Form(""),
            p_date: str = Form(""), p_time: str = Form(""), p_city: str = Form(""),
            p_name: str = Form(""), p_gender: str = Form("M"),
            p_tz: str = Form(""), p_lng: str = Form("")):
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    partner = None
    if p_date and p_time and (p_tz or p_city):
        partner = {"dt": datetime.strptime(f"{p_date} {p_time}", "%Y-%m-%d %H:%M"),
                   "city": p_city, "name": p_name or None, "gender": p_gender,
                   "tz": p_tz, "lng": p_lng}
    data = build_reading(dt, city, gender, persona, name=name, partner=partner, tz=tz, lng=lng)
    return render_result(data)


@app.post("/ask")
def ask_route(date: str = Form(...), time: str = Form(...), city: str = Form(""),
              persona: str = Form("warm"), question: str = Form(...),
              gender: str = Form("F"), tz: str = Form(""), lng: str = Form("")):
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    chart = _chart_tz(dt, tz, lng, city)
    return JSONResponse(_ask(chart, question, PERSONA_MAP.get(persona)))

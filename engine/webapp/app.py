"""
webapp.app — FastAPI 웹앱: 입력 폼 → 실제 엔진 계산 → 결과 페이지.
로컬 실행: uvicorn webapp.app:app --reload
배포: Cloud Run 등 서버리스(0으로 축소).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse

from saju.place import CITIES
from .reading import build_reading
from .render import render_result
from saju.place import chart_for_city
from saju.ask import ask as _ask
from .reading import PERSONA_MAP

app = FastAPI(title="Inyeon — Korean Saju")

_CITY_OPTS = "".join(f'<option>{c}</option>' for c in CITIES)
_PERSONAS = [("warm", "The Warm Guide"), ("blunt", "The Straight Talker"), ("mystic", "The Mystic")]


def _form_page() -> str:
    prad = "".join(
        f'<label class="p"><input type="radio" name="persona" value="{k}"{" checked" if k=="warm" else ""}> {v}</label>'
        for k, v in _PERSONAS)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Inyeon — your reading</title>
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
.row{{display:flex;gap:10px}} .row>div{{flex:1}}
button{{width:100%;background:#e8c86c;color:#231b03;font-weight:600;border:none;padding:14px;border-radius:40px;margin-top:22px;font-size:15px;cursor:pointer}}
details{{margin-top:18px}} summary{{color:#e8c86c;font-size:13px;cursor:pointer}}
</style></head><body>
<form class="card" method="post" action="/reading">
  <h1>Discover your <em>Inyeon</em></h1>
  <div class="sub">Korean saju & compatibility · your missing element</div>
  <label>Your first name (optional)</label><input name="name" placeholder="Emma">
  <div class="row"><div><label>Birth date</label><input type="date" name="date" value="1990-06-21" required></div>
  <div><label>Time</label><input type="time" name="time" value="14:30" required></div></div>
  <label>Birth city</label><select name="city">{_CITY_OPTS}</select>
  <label>Gender (for name)</label><select name="gender"><option value="F">Female</option><option value="M">Male</option></select>
  <label>Choose your reader</label><div>{prad}</div>
  <details><summary>+ Add someone for compatibility</summary>
    <div class="row"><div><label>Their birth date</label><input type="date" name="p_date"></div>
    <div><label>Time</label><input type="time" name="p_time"></div></div>
    <label>Their city</label><select name="p_city"><option value=""></option>{_CITY_OPTS}</select>
    <label>Their name (optional)</label><input name="p_name" placeholder="Jihoon">
  </details>
  <button type="submit">Reveal my reading</button>
</form></body></html>"""


_LANDING = (Path(__file__).parent / "static" / "landing.html").read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def home():
    return _LANDING


@app.get("/start", response_class=HTMLResponse)
def start():
    return _form_page()


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/reading", response_class=HTMLResponse)
def reading(date: str = Form(...), time: str = Form(...), city: str = Form(...),
            gender: str = Form("F"), persona: str = Form("warm"), name: str = Form(""),
            p_date: str = Form(""), p_time: str = Form(""), p_city: str = Form(""),
            p_name: str = Form("")):
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    partner = None
    if p_date and p_time and p_city:
        partner = {"dt": datetime.strptime(f"{p_date} {p_time}", "%Y-%m-%d %H:%M"),
                   "city": p_city, "name": p_name or None}
    data = build_reading(dt, city, gender, persona, name=name, partner=partner)
    return render_result(data)


@app.post("/ask")
def ask_route(date: str = Form(...), time: str = Form(...), city: str = Form(...),
              persona: str = Form("warm"), question: str = Form(...),
              gender: str = Form("F")):
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    chart = chart_for_city(dt, city)
    return JSONResponse(_ask(chart, question, PERSONA_MAP.get(persona)))

"""
webapp.reading — 엔진 + 해석을 하나의 '리딩' 객체로 조립 (웹앱·API 공용).
"""
from __future__ import annotations

from datetime import datetime

from saju.place import chart_for_city, chart_for_place, CITIES


def _chart(dt, city, tz, lng):
    """도시 검색(tz+경도) 우선, 없으면 기존 CITIES 표 폴백(Seoul 안전망)."""
    if tz and lng not in (None, ""):
        try:
            return chart_for_place(dt, tz, float(lng))
        except Exception:
            pass
    try:
        return chart_for_city(dt, city or "Seoul")
    except Exception:
        return chart_for_city(dt, "Seoul")
from saju.interpret import Persona, render_reading, render_compat
from saju.compat import compatibility
from saju.naming import name_to_improve_compat, couple_names, premium_korean_name
from saju.daily import daily_energy
from saju.ritual import missing_ritual

PERSONA_MAP = {"warm": Persona.WARM, "blunt": Persona.BLUNT, "mystic": Persona.MYSTIC}


def build_reading(local_dt: datetime, city: str, gender: str, persona_key: str,
                  name: str | None = None, partner: dict | None = None,
                  tz: str | None = None, lng=None) -> dict:
    """솔로(+선택적 궁합) 리딩. name=본인 이름, partner={dt, city, name, gender, tz, lng}."""
    persona = PERSONA_MAP.get(persona_key, Persona.WARM)
    chart = _chart(local_dt, city, tz, lng)
    data = {
        "chart": chart,
        "persona": persona,
        "name": (name or "").strip() or None,
        "reading": render_reading(chart, persona),
        "daily": daily_energy(chart, persona=persona),
        "ritual": missing_ritual(chart),
        "inputs": {"date": local_dt.date().isoformat(),
                   "time": local_dt.strftime("%H:%M"),
                   "city": city, "gender": gender, "persona": persona_key,
                   "tz": tz or "", "lng": lng if lng not in (None, "") else ""},
    }
    nm = (name or "").strip()
    if nm:
        data["premium_name"] = premium_korean_name(chart, gender, nm).get("card")
    if partner and partner.get("dt") and (partner.get("tz") or partner.get("city")):
        pchart = _chart(partner["dt"], partner.get("city"), partner.get("tz"), partner.get("lng"))
        comp = compatibility(chart, pchart)
        rec = name_to_improve_compat(chart, pchart, gender=gender,
                                     original_name=name)
        pgender = (partner.get("gender") or "F")
        couple = couple_names(chart, pchart, self_gender=gender,
                              partner_gender=pgender, self_name=name,
                              partner_name=partner.get("name"))
        data.update({
            "partner_chart": pchart,
            "partner_name": (partner.get("name") or "").strip() or None,
            "compat": comp,
            "compat_text": render_compat(chart, pchart, persona, name_rec=rec),
            "name_rec": rec,
            "couple_names": couple,
        })
    return data

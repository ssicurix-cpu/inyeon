"""
webapp.reading — 엔진 + 해석을 하나의 '리딩' 객체로 조립 (웹앱·API 공용).
"""
from __future__ import annotations

from datetime import datetime

from saju.place import chart_for_city, CITIES
from saju.interpret import Persona, render_reading, render_compat
from saju.compat import compatibility
from saju.naming import name_to_improve_compat, couple_names
from saju.daily import daily_energy
from saju.ritual import missing_ritual

PERSONA_MAP = {"warm": Persona.WARM, "blunt": Persona.BLUNT, "mystic": Persona.MYSTIC}


def build_reading(local_dt: datetime, city: str, gender: str, persona_key: str,
                  name: str | None = None, partner: dict | None = None) -> dict:
    """솔로(+선택적 궁합) 리딩. name=본인 이름(헤더·작명), partner={dt, city, name, gender}."""
    persona = PERSONA_MAP.get(persona_key, Persona.WARM)
    chart = chart_for_city(local_dt, city)
    data = {
        "chart": chart,
        "persona": persona,
        "name": (name or "").strip() or None,
        "reading": render_reading(chart, persona),
        "daily": daily_energy(chart, persona=persona),
        "ritual": missing_ritual(chart),
        "inputs": {"date": local_dt.date().isoformat(),
                   "time": local_dt.strftime("%H:%M"),
                   "city": city, "gender": gender, "persona": persona_key},
    }
    if partner and partner.get("dt") and partner.get("city"):
        pchart = chart_for_city(partner["dt"], partner["city"])
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

"""
saju.daily — 데일리 운세 (일진 기반). 리텐션·습관 엔진.

오늘의 일주(日 간지)가 내 일간에 대해 갖는 십신 관계로 그날의 테마를 낸다.
오늘의 오행이 내 부족 원소를 채워주면 보너스. 전부 엔진으로 계산(LLM 불필요).
"""
from __future__ import annotations

from datetime import date as _date

from .core import day_pillar
from .analysis import ten_god, TenGod
from .chart import Chart
from .interpret import Persona

_THEME = {
    TenGod.BIGYEON: ("self", "a you-focused day — assert your needs, back yourself"),
    TenGod.GEOMJAE: ("self", "a bold day — act, but watch rivalries and impulse spending"),
    TenGod.SIKSIN: ("expression", "a creative day — make, speak, put your ideas out"),
    TenGod.SANGGWAN: ("expression", "an expressive day — your voice lands, just mind your edge"),
    TenGod.PYEONJAE: ("opportunity", "a good day for money moves and getting things done"),
    TenGod.JEONGJAE: ("opportunity", "a steady day for work, money and practical wins"),
    TenGod.PYEONGWAN: ("challenge", "a demanding day — pressure shows up, meet it steadily"),
    TenGod.JEONGGWAN: ("duty", "a responsible day — handle duties, structure pays off"),
    TenGod.PYEONIN: ("support", "a restful day — receive help, study, recharge"),
    TenGod.JEONGIN: ("support", "a nurturing day — lean on others, learn, rest well"),
}


def daily_energy(chart: Chart, on: _date | None = None,
                 persona: Persona = Persona.WARM) -> dict:
    on = on or _date.today()
    today = day_pillar(on)
    tg = ten_god(chart.day_master, today.stem)
    theme, base = _THEME[tg]

    supplies_missing = bool(chart.lacking) and (
        today.stem.element in chart.lacking or today.branch.element in chart.lacking)
    bonus = ""
    if supplies_missing:
        el = chart.lacking[0].en
        bonus = f" Today also carries the {el} you're missing — lean into it."

    if persona is Persona.WARM:
        text = f"Today ({today.hanja}) is {base}.{bonus} You've got it. 🤍"
    elif persona is Persona.BLUNT:
        text = f"{today.hanja} — {base}. Use it.{bonus}"
    else:
        text = f"The day turns to {today.hanja}: {base}.{bonus} ✨"

    return {"date": on.isoformat(), "ganzhi": today.hanja, "ten_god": tg,
            "theme": theme, "supplies_missing": supplies_missing, "text": text}

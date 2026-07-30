"""
saju.ask — 'Ask your 무당' (선택형 페르소나 채팅).

프로토타입: 질문을 주제로 분류하고 사주 사실(일간·강점·부족 원소)에서 답을
선택한 무당 말투로 낸다. 나중에 이 사실 + 페르소나 지침을 LLM에 넘겨
자유질의응답으로 업그레이드(인터페이스는 동일). 지금은 API 키 없이 $0.
"""
from __future__ import annotations

from .chart import Chart
from .interpret import Persona, NATURE, ELEMENT_THEME

_TOPICS = {
    "love": ["love", "relationship", "partner", "date", "dating", "marry", "romance", "crush", "ex", "soulmate"],
    "career": ["career", "job", "work", "study", "school", "business", "purpose", "success", "calling"],
    "money": ["money", "wealth", "rich", "finance", "invest", "salary", "save", "income"],
    "health": ["health", "energy", "tired", "stress", "sleep", "body", "wellness", "burnout"],
    "timing": ["when", "timing", "this year", "next year", "soon", "should i now"],
}


def _classify(q: str) -> str:
    ql = q.lower()
    for topic, kws in _TOPICS.items():
        if any(k in ql for k in kws):
            return topic
    return "general"


def _base(topic: str, chart: Chart) -> str:
    dm = chart.day_master
    nature = NATURE[dm.hanja][0]
    dom = chart.dominant
    seek = ELEMENT_THEME[chart.lacking[0]][1] if chart.lacking else None
    miss = chart.lacking[0].en if chart.lacking else None
    if topic == "love":
        s = f"In love you're {dm.polarity.en} {dm.element.en} — {nature}. You bond best with people who steady, not drain, that energy."
        if miss:
            s += f" You're missing {miss}; partners who bring it often feel like relief. Growth, not a soulmate quiz, is the real work."
        return s
    if topic == "career":
        s = f"Your strength runs in {dom.en} — {ELEMENT_THEME[dom][0]}. Work that lets you use that will feel right."
        if seek:
            s += f" Your edge is {seek} — build it and doors open."
        return s
    if topic == "money":
        return ("Money follows structure for you, not luck. Steady systems beat big gambles. "
                f"On days your chart is strong in {dom.en}, act; when it's thin, hold.")
    if topic == "health":
        s = "Your energy balances when you tend what's low."
        if miss:
            s += f" You're light on {miss} — that's the system to nourish (rest, flow, or grounding, depending on the element)."
        return s
    if topic == "timing":
        return ("Saju reads energy and timing, not fixed dates. Check your daily energy for today's read — "
                "small aligned moves beat waiting for a 'perfect' day.")
    s = f"At your core you're {dm.polarity.en} {dm.element.en} — {nature}."
    if seek:
        s += f" Your growth edge is {seek}."
    return s


def ask(chart: Chart, question: str, persona: Persona = Persona.WARM) -> dict:
    topic = _classify(question)
    base = _base(topic, chart)
    if persona is Persona.WARM:
        text = f"{base} I've got you. 🤍"
    elif persona is Persona.BLUNT:
        text = f"{base} No sugar-coating — that's the read. 😌"
    else:
        text = f"The pillars answer… {base} ✨"
    return {"topic": topic, "text": text,
            "note": "A light reading for reflection — not fixed fate."}

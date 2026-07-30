"""
saju.ritual — '없는 원소' 리추얼/처방 (우리 시그니처 확장·웰니스).

부족 오행을 채우는 행동가능한 correspondences: 색·활동·방위·맛·실천·키워드.
CHANI식 리추얼을 우리 Missing Element 컨셉으로. 전부 큐레이션 데이터(감수 확장 대상).
"""
from __future__ import annotations

from .core import Element
from .chart import Chart

RITUAL: dict[Element, dict] = {
    Element.WOOD: {
        "keyword": "grow", "color": "green", "direction": "east", "time": "early morning",
        "activities": ["time in nature or with plants", "start a new project", "learn something"],
        "practice": "put down one small root today — plant, plan, or begin.",
    },
    Element.FIRE: {
        "keyword": "shine", "color": "red", "direction": "south", "time": "noon",
        "activities": ["move your body", "see people", "do something joyful and visible"],
        "practice": "let yourself be seen — share, connect, light something up.",
    },
    Element.EARTH: {
        "keyword": "ground", "color": "warm yellow / ochre", "direction": "center", "time": "afternoon",
        "activities": ["cook", "tidy your space", "keep a simple routine"],
        "practice": "slow down and build something solid — one steady, grounding habit.",
    },
    Element.METAL: {
        "keyword": "refine", "color": "white / gold", "direction": "west", "time": "evening",
        "activities": ["declutter", "breathwork", "set a clear boundary"],
        "practice": "cut what drains you — clear space, sharpen one clean decision.",
    },
    Element.WATER: {
        "keyword": "flow", "color": "deep blue / black", "direction": "north", "time": "night",
        "activities": ["rest", "a bath or time near water", "journal your intuition"],
        "practice": "soften and let go — rest, reflect, trust your gut.",
    },
}


def missing_ritual(chart: Chart) -> dict:
    """부족 원소(없으면 최소 원소)의 리추얼."""
    if chart.lacking:
        el = chart.lacking[0]
    else:
        el = min(chart.element_counts, key=lambda e: chart.element_counts[e])
    data = dict(RITUAL[el])
    data["element"] = el
    data["element_en"] = el.en
    return data

"""
해석 레이어 검증.

가드레일 테스트:
  - 사실 불변: 부족 원소가 3 페르소나 모두에 등장.
  - 페르소나별 출력이 서로 다름.
  - 비파국: 어떤 페르소나도 해로운/절망 표현을 쓰지 않음.
"""
from datetime import datetime

from saju.place import chart_for_city
from saju.interpret import Persona, build_facts, render_reading, render_compat
from saju.naming import name_to_improve_compat

BANNED = ["doomed", "hopeless", "you can't", "no hope", "worthless", "give up", "you're broken"]


def _jihoon():
    return chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")   # 庚, 水 부족

def _emma():
    return chart_for_city(datetime(1990, 6, 21, 14, 30), "New York")  # 丁, 木 부족


def test_facts_deterministic():
    f = build_facts(_jihoon())
    assert f["element"] == "Metal"
    assert f["missing"].en == "Water"


def test_fact_invariant_across_personas():
    # 부족 원소(Water)가 세 페르소나 모두에 등장 → 사실 불변
    for p in Persona:
        assert "Water" in render_reading(_jihoon(), p)


def test_personas_differ():
    outs = {render_reading(_jihoon(), p) for p in Persona}
    assert len(outs) == 3


def test_no_doom_language():
    for chart in (_jihoon(), _emma()):
        for p in Persona:
            text = render_reading(chart, p).lower()
            assert not any(b in text for b in BANNED)


def test_compat_reading_constructive_and_persona():
    a, b = _emma(), _jihoon()
    rec = name_to_improve_compat(a, b, gender="F", original_name="Emma")
    outs = []
    for p in Persona:
        s = render_compat(a, b, p, name_rec=rec)
        assert "%" in s
        assert not any(x in s.lower() for x in BANNED)
        outs.append(s)
    assert len(set(outs)) == 3  # 페르소나별 상이

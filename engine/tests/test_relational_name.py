"""
'이름으로 궁합 튜닝' 검증 (핵심 결제 전환 메커니즘).

Emma(火) × Jihoon(金) = 상극(火극金) → 통관 오행 = 土.
→ 土를 공급하는 이름 추천, 궁합 점수 boosted > base.
"""
from datetime import datetime

from saju.core import Element
from saju.place import chart_for_city
from saju.naming import harmonizing_element, name_to_improve_compat


def _emma():
    return chart_for_city(datetime(1990, 6, 21, 14, 30), "New York")   # 丁 火

def _jihoon():
    return chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")       # 庚 金

def _oliver():
    return chart_for_city(datetime(1985, 12, 10, 9, 0), "London")      # 癸 水


def test_harmonizing_element_is_mediator_for_controlling_pair():
    # 火(Emma) 극 金(Jihoon) → 통관 土
    assert harmonizing_element(_emma(), _jihoon()) is Element.EARTH


def test_harmonizing_element_for_non_controlling_pair():
    # 지훈(金) 지훈... 상생/비화면 함께 약한 오행 반환 (에러 없이 Element)
    target = harmonizing_element(_jihoon(), _oliver())
    assert isinstance(target, Element)


def test_name_improves_compatibility():
    res = name_to_improve_compat(_emma(), _jihoon(), gender="F", original_name="Emma")
    assert res["relation_type"] == "상극"
    assert res["harmonizing_element"] is Element.EARTH
    assert res["best"] is not None
    assert res["best"].supplies(Element.EARTH)     # 추천 이름은 土 공급
    assert res["boosted_score"] > res["base_score"]
    assert res["boosted_score"] <= 100
    assert "→" in res["reasoning_en"]


def test_candidates_all_supply_target():
    res = name_to_improve_compat(_emma(), _jihoon(), gender="F")
    for n in res["candidates"]:
        assert n.supplies(res["harmonizing_element"])

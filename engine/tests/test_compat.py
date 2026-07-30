"""
궁합 계산 검증.

관계 표(삼합/육합/충, 상생/상극/비화)는 정의라 확정적으로 검증.
통합: 지훈(庚,午,水부족) × Oliver(癸,丑,金부족) → 상생 + 오행 상호보완 → 고득점.
"""
from datetime import datetime

from saju.core import STEMS, BRANCHES, Element
from saju.place import chart_for_city
from saju.compat import (
    day_master_relation, zodiac_relation, element_complement, compatibility,
)


# --- 띠 관계 (정의) ----------------------------------------------------------

def test_zodiac_relations():
    assert zodiac_relation(BRANCHES[6], BRANCHES[7])["type"] == "육합"   # 午-未
    assert zodiac_relation(BRANCHES[0], BRANCHES[6])["type"] == "충"     # 子-午
    assert zodiac_relation(BRANCHES[8], BRANCHES[0])["type"] == "삼합"   # 申-子(辰)
    assert zodiac_relation(BRANCHES[6], BRANCHES[1])["type"] == "무"     # 午-丑


# --- 일간 관계 (정의) --------------------------------------------------------

def test_day_master_relations():
    # 庚(金) → 癸(水): 金生水 상생
    assert day_master_relation(STEMS[6], STEMS[9])["type"] == "상생"
    # 丁(火) → 庚(金): 火克金 상극
    assert day_master_relation(STEMS[3], STEMS[6])["type"] == "상극"
    # 庚-庚: 비화
    assert day_master_relation(STEMS[6], STEMS[6])["type"] == "비화"


# --- 오행 상호보완 + 통합 ----------------------------------------------------

def _jihoon():
    return chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")     # 庚, 午, 水부족

def _oliver():
    return chart_for_city(datetime(1985, 12, 10, 9, 0), "London")    # 癸, 丑, 金부족


def test_element_complement_mutual():
    comp = element_complement(_jihoon(), _oliver())
    assert Element.METAL in comp["a_fills_b"]   # 지훈 금3 → Oliver 금부족 채움
    assert Element.WATER in comp["b_fills_a"]   # Oliver 수2 → 지훈 수부족 채움
    assert comp["mutual"] is True


def test_compatibility_high_for_complementary_pair():
    c = compatibility(_jihoon(), _oliver())
    assert c.day_master["type"] == "상생"
    assert c.complement["mutual"] is True
    assert c.score >= 90
    assert "%" in c.headline_en


def test_compatibility_symmetric_score():
    a, b = _jihoon(), _oliver()
    assert compatibility(a, b).score == compatibility(b, a).score


def test_compatibility_serializable():
    import json
    c = compatibility(_jihoon(), _oliver())
    s = json.dumps(c.to_dict(), ensure_ascii=False)
    assert "score" in s and "Metal" in s

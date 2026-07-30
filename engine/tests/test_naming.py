"""
이름 작명 검증.

발음오행(결정론적)과 '부족 오행 보완' 선별 규칙을 확인.
표준 케이스(지훈, 서울)=水 부족, 뉴욕(Emma)=木 부족, 런던(Oliver)=金 부족.
"""
from datetime import datetime

from saju.core import Element
from saju.place import chart_for_city
from saju.naming.phonetics import sound_element, name_sound_elements
from saju.naming import target_element, premium_korean_name, koreanize


# --- 발음오행 (정확) ---------------------------------------------------------

def test_sound_element_basic():
    assert sound_element("지") is Element.METAL   # ㅈ=금
    assert sound_element("훈") is Element.EARTH    # ㅎ=토
    assert sound_element("민") is Element.WATER    # ㅁ=수
    assert sound_element("가") is Element.WOOD     # ㄱ=목
    assert sound_element("도") is Element.FIRE     # ㄷ=화
    assert sound_element("A") is None              # 한글 아님


def test_name_sound_elements():
    assert name_sound_elements("민준") == [Element.WATER, Element.METAL]
    assert name_sound_elements("지훈") == [Element.METAL, Element.EARTH]


# --- 부족 오행 보완 (하드 필터) ---------------------------------------------

def test_premium_name_supplies_lacking_element():
    # 서울 케이스: 水 부족 → 추천 이름은 반드시 水(ㅁㅂㅍ) 소리를 포함
    chart = chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")
    assert chart.lacking == [Element.WATER]
    res = premium_korean_name(chart, gender="M", original_name="Jihoon")
    assert res["target_element"] is Element.WATER
    assert res["best"] is not None
    assert res["best"].supplies(Element.WATER)


def test_premium_name_newyork_lacks_wood():
    chart = chart_for_city(datetime(1990, 6, 21, 14, 30), "New York")
    assert chart.lacking == [Element.WOOD]
    res = premium_korean_name(chart, gender="F", original_name="Emma")
    assert res["best"].supplies(Element.WOOD)   # 木(ㄱㅋ) 소리 포함


def test_koreanize_surname_matches_lacking():
    chart = chart_for_city(datetime(1985, 12, 10, 9, 0), "London")  # 金 부족
    assert chart.lacking == [Element.METAL]
    res = koreanize("Oliver", chart)
    assert res["target_element"] is Element.METAL
    # 붙인 성은 모두 金(ㅅㅈㅊ) 발음오행
    from saju.naming.phonetics import sound_element as se
    for opt in res["options"]:
        surname = opt.split()[0]
        assert se(surname) is Element.METAL


def test_gender_filter():
    chart = chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")
    res = premium_korean_name(chart, gender="F", original_name="Sujin")
    for n in res["candidates"]:
        assert n.gender in ("F", "U")

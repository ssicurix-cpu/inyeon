"""
정의 코어 + 일주 계산 검증.

일주 앵커(offset=14)는 독립 라이브러리 sxtwl(寿星天文历)로 뽑은 정답지와 대조한다.
아래 EXPECTED_DAY_PILLARS 는 sxtwl 기준 검증값 (2026-07-30 등 5개 날짜).
"""
from datetime import date

from saju.core import (
    STEMS, BRANCHES, GanZhi, ganzhi_from_index, day_pillar, HIDDEN_STEMS, Element,
)


# --- 정의 무결성 -------------------------------------------------------------

def test_counts():
    assert len(STEMS) == 10
    assert len(BRANCHES) == 12


def test_element_distribution_in_stems():
    # 천간: 각 오행 2개씩 (양/음)
    from collections import Counter
    c = Counter(s.element for s in STEMS)
    assert all(v == 2 for v in c.values())
    assert set(c) == set(Element)


def test_sexagenary_cycle_is_bijective():
    # 0..59 → GanZhi → index 왕복이 항등
    seen = set()
    for i in range(60):
        gz = ganzhi_from_index(i)
        assert gz.sexagenary_index == i
        seen.add((gz.stem.index, gz.branch.index))
    assert len(seen) == 60  # 60갑자 모두 유일


def test_hidden_stems_cover_all_branches():
    assert set(HIDDEN_STEMS) == set(range(12))
    for stems in HIDDEN_STEMS.values():
        assert all(0 <= s <= 9 for s in stems)


# --- 일주 검증 (sxtwl 정답지) -----------------------------------------------

# (year, month, day) -> 일주 한자. sxtwl 기준 검증값.
EXPECTED_DAY_PILLARS = {
    (1990, 5, 15): "庚辰",
    (2000, 1, 1): "戊午",
    (2024, 1, 1): "甲子",
    (1984, 2, 2): "丙寅",
    (2026, 7, 30): "乙巳",
}


def test_day_pillar_matches_ground_truth():
    for (y, m, d), expected in EXPECTED_DAY_PILLARS.items():
        got = day_pillar(date(y, m, d)).hanja
        assert got == expected, f"{y}-{m}-{d}: got {got}, expected {expected}"


def test_day_pillar_advances_by_one_each_day():
    # 연속 60일이면 60갑자 한 바퀴
    d0 = date(2024, 1, 1)  # 甲子
    idx0 = day_pillar(d0).sexagenary_index
    assert idx0 == 0
    for k in range(1, 61):
        idx = day_pillar(date.fromordinal(d0.toordinal() + k)).sexagenary_index
        assert idx == k % 60


def test_main_case_day_master():
    # 1990-05-15 서울 → 일간(Day Master) 庚 (Metal)
    dp = day_pillar(date(1990, 5, 15))
    assert dp.stem.hanja == "庚"
    assert dp.stem.element is Element.METAL

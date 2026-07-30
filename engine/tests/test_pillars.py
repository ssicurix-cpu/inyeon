"""
연주+띠, 월주 검증.

정답지: 표준 케이스(1990-05-15 06:30 서울) = 庚午년 辛巳월, 말(午)띠.
립춘 경계 롤오버, 알려진 연주(2024=甲辰, 2026=丙午)도 확인.
KST(UTC+9) → UTC 변환 후 입력.
"""
from datetime import datetime, timedelta

from saju.pillars import (
    year_pillar, month_pillar, zodiac_branch, ipchun_utc, saju_year,
)


def kst_to_utc(y, mo, d, h, mi=0):
    return datetime(y, mo, d, h, mi) - timedelta(hours=9)


# --- 표준 케이스 -------------------------------------------------------------

def test_main_case_year_month():
    dt = kst_to_utc(1990, 5, 15, 6, 30)
    assert year_pillar(dt).hanja == "庚午"
    assert month_pillar(dt).hanja == "辛巳"


def test_main_case_zodiac_is_horse():
    dt = kst_to_utc(1990, 5, 15, 6, 30)
    z = zodiac_branch(dt)
    assert z.hanja == "午"
    assert z.animal_en == "Horse"
    assert z.animal_ko == "말"


# --- 립춘 경계 롤오버 (2000 립춘 ≈ KST 2000-02-04 21:40) ---------------------

def test_ipchun_boundary_rolls_year_and_month():
    before = kst_to_utc(2000, 2, 4, 19, 0)   # 립춘 전
    after = kst_to_utc(2000, 2, 4, 23, 0)    # 립춘 후
    # 립춘 전: 己卯년(1999 사주년), 丑월
    assert year_pillar(before).hanja == "己卯"
    assert month_pillar(before).branch.hanja == "丑"
    # 립춘 후: 庚辰년(2000 사주년), 寅월
    assert year_pillar(after).hanja == "庚辰"
    assert month_pillar(after).branch.hanja == "寅"


def test_saju_year_switches_at_ipchun():
    y = 2000
    ic = ipchun_utc(y)
    assert saju_year(ic - timedelta(minutes=1)) == y - 1
    assert saju_year(ic + timedelta(minutes=1)) == y


# --- 알려진 연주 -------------------------------------------------------------

def test_known_year_pillars():
    # 立春 지난 시점(각 연도 3월)로 확인
    assert year_pillar(datetime(2024, 3, 1)).hanja == "甲辰"
    assert year_pillar(datetime(2026, 3, 1)).hanja == "丙午"  # 2026 = 붉은 말띠


def test_ipchun_is_early_february():
    for y in (1984, 1990, 2000, 2024, 2026):
        ic = ipchun_utc(y)
        assert ic.month == 2
        assert 2 <= ic.day <= 5

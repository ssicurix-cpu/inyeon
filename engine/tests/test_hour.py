"""
진태양시 + 시주 검증.

표준 케이스 1990-05-15 06:30 서울(경도 126.978E, KST=UTC+9)
  → 진태양시 ≈ 06:01, 시주 己卯 (정답지).
자시 경계·시지 경계·균시차도 확인. 본 엔진의 '표준 자시 규칙'을 명시적으로 테스트.
"""
from datetime import datetime, timedelta

from saju.core import GanZhi, STEMS, BRANCHES, day_pillar
from saju.hour import (
    equation_of_time_min, true_solar_datetime, hour_branch_index,
    hour_pillar, day_and_hour_pillars,
)

SEOUL_LON = 126.9780


def kst_to_utc(y, mo, d, h, mi=0):
    return datetime(y, mo, d, h, mi) - timedelta(hours=9)


# --- 균시차 -----------------------------------------------------------------

def test_equation_of_time_known_values():
    assert abs(equation_of_time_min(datetime(2024, 2, 11, 12)) - (-14.2)) < 1.0
    assert abs(equation_of_time_min(datetime(2024, 11, 3, 12)) - (16.5)) < 1.0
    assert abs(equation_of_time_min(datetime(2024, 4, 15, 12)) - (0.0)) < 1.0


# --- 진태양시 보정 -----------------------------------------------------------

def test_true_solar_time_seoul_offset():
    # 서울 06:30 KST → 진태양시 ≈ 06:01 (약 -29분: 경도 -32분 + EoT +3.6분)
    ts = true_solar_datetime(kst_to_utc(1990, 5, 15, 6, 30), SEOUL_LON)
    assert ts.date().isoformat() == "1990-05-15"
    minutes = ts.hour * 60 + ts.minute
    assert abs(minutes - (6 * 60 + 1)) <= 2


# --- 표준 케이스 시주 --------------------------------------------------------

def test_main_case_hour_pillar():
    dp, hp, ts = day_and_hour_pillars(kst_to_utc(1990, 5, 15, 6, 30), SEOUL_LON)
    assert dp.hanja == "庚辰"
    assert hp.hanja == "己卯"


# --- 시지 경계 (진태양시 직접 입력) -----------------------------------------

def test_hour_branch_boundaries():
    def b(h, mi):
        return hour_branch_index(datetime(2000, 1, 1, h, mi))
    assert b(23, 30) == 0   # 子 (23~01)
    assert b(0, 30) == 0    # 子
    assert b(1, 0) == 1     # 丑 (01~03)
    assert b(5, 30) == 3    # 卯 (05~07)
    assert b(6, 30) == 3    # 卯
    assert b(11, 0) == 6    # 午 (11~13)
    assert b(22, 0) == 11   # 亥 (21~23)


# --- 표준 자시(子時) 규칙 명시 검증 -----------------------------------------

def test_standard_zi_hour_rule():
    # 庚일 23:30(진태양시) → 표준 방식: 당일 일간 庚 → 子시干 (6*2%10=2=丙) → 丙子
    gyeong_day = day_pillar(datetime(1990, 5, 15).__class__(1990, 5, 15))  # 庚辰
    assert gyeong_day.hanja == "庚辰"
    hp = hour_pillar(gyeong_day, datetime(1990, 5, 15, 23, 30))
    assert hp.hanja == "丙子"

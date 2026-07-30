"""
saju.hour — 진태양시 + 시주(時柱) (Slice 4)

시주는 '진태양시(true/apparent solar time)' 기준으로 정한다.
  진태양시 = UTC + 경도보정(경도/15시간) + 균시차(EoT)
  - 경도보정: 표준자오선이 아니라 실제 출생 경도 기준(글로벌 필수).
  - 균시차(EoT): 겉보기-평균 태양시 차이(±16분). astronomy-engine으로 계산,
    공표값과 분 단위 일치 확인(2월 ≈ -14, 5월 ≈ +4, 11월 ≈ +16.5분).

시지(時支): 진태양시 2시간 단위. 子=23~01, 丑=01~03, ... 亥=21~23.
시간(時干): 일간에서 五鼠遁으로 도출. 子시干 = (일간*2)%10, 이후 시지마다 +1.

**자시(子時) 경계 규칙(중요·유파차):** 본 엔진 기본값은 **표준 방식** —
일주 경계는 (진태양시) 자정 00:00, 子시(23~01)는 각자 그 순간의 '진태양시 날짜'의
일간을 그대로 쓴다. 즉 23:30 출생은 당일 일간으로 丙子(예: 庚일→丙子),
00:30 출생은 다음날 일간으로 계산. 일부 만세력이 쓰는 야자시(晚子時, 23~24시에
익일 일간 사용) 방식과 다를 수 있음 → 향후 옵션화 대상(Leo 확인 필요).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import astronomy

from .core import GanZhi, STEMS, BRANCHES, day_pillar


def equation_of_time_min(dt_utc: datetime) -> float:
    """균시차(분). 겉보기 태양시 - 평균 태양시."""
    t = astronomy.Time.Make(dt_utc.year, dt_utc.month, dt_utc.day,
                            dt_utc.hour, dt_utc.minute, dt_utc.second)
    obs = astronomy.Observer(0, 0, 0)
    ra = astronomy.Equator(astronomy.Body.Sun, t, obs, True, True).ra  # hours, of date
    gast = astronomy.SiderealTime(t)                                   # hours
    ast = (gast - ra + 12) % 24        # Greenwich 겉보기 태양시(시)
    ut = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600
    return ((ast - ut + 12) % 24 - 12) * 60


def true_solar_datetime(dt_utc: datetime, longitude_east: float,
                        apparent: bool = True) -> datetime:
    """출생 순간(UTC) + 출생 경도 → 진태양시 벽시계(naive datetime).

    apparent=True 면 균시차 포함(진태양시), False 면 평태양시(경도 보정만).
    """
    ts = dt_utc + timedelta(hours=longitude_east / 15.0)
    if apparent:
        ts = ts + timedelta(minutes=equation_of_time_min(dt_utc))
    return ts


def hour_branch_index(solar_dt: datetime) -> int:
    """진태양시 → 시지 index (0=子 .. 11=亥). 子시는 23~01시."""
    t = solar_dt.hour + solar_dt.minute / 60 + solar_dt.second / 3600
    return int((t + 1) // 2) % 12


def hour_pillar(day_gz: GanZhi, solar_dt: datetime) -> GanZhi:
    """시주. day_gz=진태양시 날짜의 일주, solar_dt=진태양시."""
    hb = hour_branch_index(solar_dt)
    rat_stem = (day_gz.stem.index * 2) % 10        # 五鼠遁: 子시 천간
    stem_index = (rat_stem + hb) % 10
    return GanZhi(STEMS[stem_index], BRANCHES[hb])


def day_and_hour_pillars(dt_utc: datetime, longitude_east: float,
                         apparent: bool = True) -> tuple[GanZhi, GanZhi, datetime]:
    """UTC+경도 → (일주, 시주, 진태양시). 일주는 진태양시 날짜 기준."""
    ts = true_solar_datetime(dt_utc, longitude_east, apparent)
    dp = day_pillar(ts.date())
    hp = hour_pillar(dp, ts)
    return dp, hp, ts

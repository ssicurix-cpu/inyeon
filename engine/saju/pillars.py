"""
saju.pillars — 연주(年柱)+띠, 월주(月柱) (Slice 3)

절기는 '태양의 겉보기 황경(apparent ecliptic longitude)'으로 정의된다.
  - 12 節(월 경계)은 황경 315°(立春)부터 30°마다: 315→寅, 345→卯, 15→辰 ...
  - 연주는 立春(315°) 기준으로 바뀐다(양력 1/1도, 설날도 아님).

계산은 astronomy-engine(순수 파이썬, 외부 데이터파일 불필요 → 서버리스 적합)으로
황경을 구한다. 정확도는 공표 절기 시각과 분 단위로 일치함을 확인했다(예: 立春 2024
= UTC 08:26, 베이징 16:27). tests/test_pillars.py 로 고정.

입력 계약: `dt_utc` 는 출생 순간을 **UTC(naive datetime)** 로 준 것.
로컬시각→UTC 변환, 진태양시 보정은 이후 슬라이스(시주/시간대)에서 처리한다.
"""
from __future__ import annotations

from datetime import datetime

import astronomy

from .core import GanZhi, Branch, BRANCHES, ganzhi_from_index

# 12 節의 월지 시작: 立春(315°) → 寅(index 2). 30°마다 지지 +1.
_MONTH_BRANCH_START = 2   # 寅
_IPCHUN_LON = 315.0


def sun_longitude(dt_utc: datetime) -> float:
    """출생 순간(UTC)의 태양 겉보기 황경(도, 0~360)."""
    t = astronomy.Time.Make(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour, dt_utc.minute, dt_utc.second + dt_utc.microsecond / 1e6,
    )
    return astronomy.SunPosition(t).elon


def ipchun_utc(year: int) -> datetime:
    """해당 양력 연도의 立春(황경 315° 도달) 순간 (UTC, naive)."""
    start = astronomy.Time.Make(year, 1, 20, 0, 0, 0)
    return astronomy.SearchSunLongitude(_IPCHUN_LON, start, 30).Utc()


def _month_sector(dt_utc: datetime) -> int:
    """立春(寅)=0, 驚蟄(卯)=1 ... 로 세는 월 순번 (0~11)."""
    lon = sun_longitude(dt_utc)
    return int(((lon - _IPCHUN_LON) % 360) // 30)


def saju_year(dt_utc: datetime) -> int:
    """立春 기준 사주 연도. 立春 이전 출생이면 전년."""
    y = dt_utc.year
    return y if dt_utc >= ipchun_utc(y) else y - 1


def year_pillar(dt_utc: datetime) -> GanZhi:
    """연주(年柱). 立春 기준."""
    return ganzhi_from_index((saju_year(dt_utc) - 4) % 60)


def zodiac_branch(dt_utc: datetime) -> Branch:
    """띠 = 연주의 지지 (立春 기준)."""
    return year_pillar(dt_utc).branch


def month_pillar(dt_utc: datetime) -> GanZhi:
    """월주(月柱). 월지=절기 순번, 월간=五虎遁(연간에서 도출)."""
    sector = _month_sector(dt_utc)
    branch_index = (_MONTH_BRANCH_START + sector) % 12
    year_stem_index = year_pillar(dt_utc).stem.index
    # 五虎遁: 寅월 천간 = (연간*2 + 2) % 10, 이후 절기마다 +1
    tiger_stem = (year_stem_index * 2 + 2) % 10
    stem_index = (tiger_stem + sector) % 10
    from .core import STEMS
    return GanZhi(STEMS[stem_index], BRANCHES[branch_index])

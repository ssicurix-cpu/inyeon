"""
saju.lunar — 음력 생일 변환 (Slice 5)

무료 훅/가입 유인용 '음력 생일'. 한국 음력 기준(korean_lunar_calendar, 순수 파이썬).
사주 8글자는 절기 기반이라 음력이 필요 없지만, 음력 생일은 사용자에게 보여주는 값.
입력은 사용자의 '실제 양력 생일(civil date)'.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from korean_lunar_calendar import KoreanLunarCalendar


@dataclass(frozen=True)
class LunarDate:
    year: int
    month: int
    day: int
    is_leap_month: bool  # 윤달 여부

    def __str__(self) -> str:
        leap = " (윤달/leap)" if self.is_leap_month else ""
        return f"{self.year}-{self.month:02d}-{self.day:02d}{leap}"


def to_lunar(solar: date) -> LunarDate:
    """양력 생일 → 음력 생일."""
    k = KoreanLunarCalendar()
    k.setSolarDate(solar.year, solar.month, solar.day)
    return LunarDate(k.lunarYear, k.lunarMonth, k.lunarDay, bool(k.isIntercalation))

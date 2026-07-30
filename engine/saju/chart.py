"""
saju.chart — 전체 사주 차트 조립 (Slice 5 capstone)

무료 훅이 호출하는 최종 계산 함수. 4기둥 + 일간 + 오행 분포 + 십신 + 띠 + 음력.

입력(임시 계약): local_dt(출생 벽시계, naive) + utc_offset_hours + longitude_east.
Slice 6에서 (출생지 → IANA 시간대/DST/경도) 자동 해석으로 대체 예정.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .core import GanZhi, Element
from .pillars import year_pillar, month_pillar
from .hour import day_and_hour_pillars
from .analysis import (
    TenGod, ten_god, element_counts, lacking_elements, dominant_element,
)
from .lunar import to_lunar, LunarDate


@dataclass
class Chart:
    pillars: dict[str, GanZhi]              # year/month/day/hour
    day_master: object                      # Stem
    element_counts: dict[Element, int]
    lacking: list[Element]
    dominant: Element
    ten_gods: dict[str, object]             # year/month/hour → TenGod (day=None)
    zodiac: object                          # Branch (띠)
    lunar: LunarDate
    true_solar_time: datetime

    def eight_char(self) -> str:
        p = self.pillars
        return f"{p['year']} {p['month']} {p['day']} {p['hour']}"

    def to_dict(self) -> dict:
        def gz(g: GanZhi) -> dict:
            return {
                "ganzhi": g.hanja, "ko": g.ko,
                "stem": {"hanja": g.stem.hanja, "ko": g.stem.ko,
                         "element": g.stem.element.en, "polarity": g.stem.polarity.en},
                "branch": {"hanja": g.branch.hanja, "ko": g.branch.ko,
                           "element": g.branch.element.en,
                           "animal": g.branch.animal_en},
            }
        return {
            "pillars": {k: gz(v) for k, v in self.pillars.items()},
            "eight_char": self.eight_char(),
            "day_master": {
                "hanja": self.day_master.hanja, "ko": self.day_master.ko,
                "element_en": self.day_master.element.en,
                "element_ko": self.day_master.element.ko,
                "polarity": self.day_master.polarity.en,
            },
            "five_elements": {e.en: n for e, n in self.element_counts.items()},
            "lacking": [e.en for e in self.lacking],
            "dominant": self.dominant.en,
            "ten_gods": {
                k: (None if v is None else {"ko": v.ko, "hanja": v.hanja, "en": v.en})
                for k, v in self.ten_gods.items()
            },
            "zodiac": {"hanja": self.zodiac.hanja,
                       "animal_ko": self.zodiac.animal_ko,
                       "animal_en": self.zodiac.animal_en},
            "lunar_birthday": {"year": self.lunar.year, "month": self.lunar.month,
                               "day": self.lunar.day, "leap": self.lunar.is_leap_month},
            "true_solar_time": self.true_solar_time.isoformat(),
        }


def compute_chart(local_dt: datetime, utc_offset_hours: float,
                  longitude_east: float) -> Chart:
    """출생 로컬시각 + UTC오프셋 + 경도 → 전체 사주 차트."""
    dt_utc = local_dt - timedelta(hours=utc_offset_hours)

    yp = year_pillar(dt_utc)
    mp = month_pillar(dt_utc)
    dp, hp, ts = day_and_hour_pillars(dt_utc, longitude_east)
    pillars = {"year": yp, "month": mp, "day": dp, "hour": hp}

    dm = dp.stem
    counts = element_counts(pillars)
    tg = {
        "year": ten_god(dm, yp.stem),
        "month": ten_god(dm, mp.stem),
        "day": None,  # 日主 (자기 자신)
        "hour": ten_god(dm, hp.stem),
    }
    return Chart(
        pillars=pillars,
        day_master=dm,
        element_counts=counts,
        lacking=lacking_elements(counts),
        dominant=dominant_element(counts),
        ten_gods=tg,
        zodiac=yp.branch,
        lunar=to_lunar(local_dt.date()),
        true_solar_time=ts,
    )

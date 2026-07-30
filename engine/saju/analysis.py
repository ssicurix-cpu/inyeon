"""
saju.analysis — 오행 분포 + 십신(Ten Gods) (Slice 5)

- 오행 분포: 사주 8글자(천간4+지지4)의 오행을 센다(가장 설명하기 쉬운 표준 방식).
  부족/과다 오행은 용신·이름 작명(부족 오행 보완)에 사용.
- 십신: 각 천간이 일간(Day Master)에 대해 갖는 관계. 오행 생극 + 음양 일치로 결정.
"""
from __future__ import annotations

from enum import Enum

from .core import Element, Stem, GanZhi

# 오행 상생 순서: 木→火→土→金→水→(木). 다음 원소 = 내가 생하는 것.
_GEN_ORDER = (Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER)


def generates(e: Element) -> Element:
    """e가 생(生)하는 오행. 木→火→土→金→水→木."""
    return _GEN_ORDER[(_GEN_ORDER.index(e) + 1) % 5]


def controls(e: Element) -> Element:
    """e가 극(克)하는 오행. 木克土, 土克水, 水克火, 火克金, 金克木."""
    return _GEN_ORDER[(_GEN_ORDER.index(e) + 2) % 5]


# 하위호환 별칭
_generates = generates
_controls = controls


class TenGod(Enum):
    """십신. (한글, 한자, 영어)"""
    BIGYEON = ("비견", "比肩", "Companion")
    GEOMJAE = ("겁재", "劫財", "Rob Wealth")
    SIKSIN = ("식신", "食神", "Eating God")
    SANGGWAN = ("상관", "傷官", "Hurting Officer")
    PYEONJAE = ("편재", "偏財", "Indirect Wealth")
    JEONGJAE = ("정재", "正財", "Direct Wealth")
    PYEONGWAN = ("편관", "偏官", "Seven Killings")   # 七殺
    JEONGGWAN = ("정관", "正官", "Direct Officer")
    PYEONIN = ("편인", "偏印", "Indirect Resource")
    JEONGIN = ("정인", "正印", "Direct Resource")

    def __init__(self, ko: str, hanja: str, en: str):
        self.ko = ko
        self.hanja = hanja
        self.en = en


def ten_god(day_master: Stem, other: Stem) -> TenGod:
    """일간(day_master)에 대한 other 천간의 십신."""
    dm, x = day_master.element, other.element
    same_pol = day_master.polarity is other.polarity
    if x is dm:
        return TenGod.BIGYEON if same_pol else TenGod.GEOMJAE
    if _generates(dm) is x:          # 일간이 x를 생 → 식상
        return TenGod.SIKSIN if same_pol else TenGod.SANGGWAN
    if _controls(dm) is x:           # 일간이 x를 극 → 재성
        return TenGod.PYEONJAE if same_pol else TenGod.JEONGJAE
    if _controls(x) is dm:           # x가 일간을 극 → 관성
        return TenGod.PYEONGWAN if same_pol else TenGod.JEONGGWAN
    # x가 일간을 생 → 인성
    return TenGod.PYEONIN if same_pol else TenGod.JEONGIN


def element_counts(pillars: dict[str, GanZhi]) -> dict[Element, int]:
    """사주 8글자(천간4+지지4)의 오행 분포. 5원소 모두 키로 포함(0 채움)."""
    counts = {e: 0 for e in Element}
    for gz in pillars.values():
        counts[gz.stem.element] += 1
        counts[gz.branch.element] += 1
    return counts


def lacking_elements(counts: dict[Element, int]) -> list[Element]:
    """분포가 0인 오행(용신 보완·작명 대상)."""
    return [e for e, n in counts.items() if n == 0]


def dominant_element(counts: dict[Element, int]) -> Element:
    """가장 많은 오행."""
    return max(counts, key=lambda e: counts[e])

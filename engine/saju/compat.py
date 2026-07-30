"""
saju.compat — 궁합(Compatibility) 계산 (간판 훅)

두 사람 사주 → 세 레이어:
  1. 일간(Day Master) 오행 관계 — 코어. 상생/비화/상극.
  2. 띠(연지) 관계 — 삼합/육합/충 (서양인에게 친숙한 접근층).
  3. 오행 상호보완 — 한쪽의 부족을 다른 쪽이 채워주나.

점수(0~100)는 엔터테인먼트용 투명 합성값. 진짜 가치는 근거가 있는 '구성요소'다.
"""
from __future__ import annotations

from dataclasses import dataclass

from .core import Stem, Branch, Element
from .analysis import generates, controls
from .chart import Chart

# 띠(지지) 관계 표 (index 0=子 .. 11=亥)
_SAMHAP = [{8, 0, 4}, {11, 3, 7}, {2, 6, 10}, {5, 9, 1}]  # 申子辰 亥卯未 寅午戌 巳酉丑
_YUKHAP = {frozenset(p) for p in [(0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]}


def day_master_relation(a: Stem, b: Stem) -> dict:
    """두 일간의 오행 관계."""
    ea, eb = a.element, b.element
    if ea is eb:
        return {"type": "비화", "type_en": "Similar", "direction": None,
                "ko": f"둘 다 {ea.ko} 일간 — 결이 비슷해 편하지만 닮은 만큼 경쟁도.",
                "en": f"Both {ea.en} Day Masters — familiar and easy, but similar energy can compete."}
    if generates(ea) is eb:
        return {"type": "상생", "type_en": "Generating", "direction": "a->b",
                "ko": f"A의 {ea.ko}가 B의 {eb.ko}를 살려줌 — 지지하고 북돋는 관계.",
                "en": f"A's {ea.en} nourishes B's {eb.en} — supportive and uplifting."}
    if generates(eb) is ea:
        return {"type": "상생", "type_en": "Generating", "direction": "b->a",
                "ko": f"B의 {eb.ko}가 A의 {ea.ko}를 살려줌 — 지지하고 북돋는 관계.",
                "en": f"B's {eb.en} nourishes A's {ea.en} — supportive and uplifting."}
    if controls(ea) is eb:
        return {"type": "상극", "type_en": "Controlling", "direction": "a->b",
                "ko": f"A의 {ea.ko}가 B의 {eb.ko}를 누름 — 끌림과 긴장이 공존.",
                "en": f"A's {ea.en} controls B's {eb.en} — magnetic but with friction."}
    return {"type": "상극", "type_en": "Controlling", "direction": "b->a",
            "ko": f"B의 {eb.ko}가 A의 {ea.ko}를 누름 — 끌림과 긴장이 공존.",
            "en": f"B's {eb.en} controls A's {ea.en} — magnetic but with friction."}


def zodiac_relation(a: Branch, b: Branch) -> dict:
    """두 띠(연지)의 관계: 삼합/육합/충/무."""
    ia, ib = a.index, b.index
    pair = frozenset({ia, ib})
    if ia != ib and any({ia, ib} <= tri for tri in _SAMHAP):
        return {"type": "삼합", "type_en": "Triple Harmony",
                "ko": f"{a.animal_ko}·{b.animal_ko} 삼합 — 강한 조화.",
                "en": f"{a.animal_en} & {b.animal_en}: Triple Harmony — strong bond."}
    if pair in _YUKHAP:
        return {"type": "육합", "type_en": "Six Harmony",
                "ko": f"{a.animal_ko}·{b.animal_ko} 육합 — 잘 맞는 짝.",
                "en": f"{a.animal_en} & {b.animal_en}: Six Harmony — a natural match."}
    if abs(ia - ib) == 6:
        return {"type": "충", "type_en": "Clash",
                "ko": f"{a.animal_ko}·{b.animal_ko} 충 — 부딪히지만 그만큼 뜨거움.",
                "en": f"{a.animal_en} & {b.animal_en}: Clash — friction, but intense chemistry."}
    return {"type": "무", "type_en": "Neutral",
            "ko": f"{a.animal_ko}·{b.animal_ko} — 특별한 충/합은 없음.",
            "en": f"{a.animal_en} & {b.animal_en}: no special clash or harmony."}


def element_complement(a: Chart, b: Chart) -> dict:
    """오행 상호보완: 한쪽 부족을 다른 쪽이 넉넉히(2+) 채우나."""
    a_fills = [e for e in b.lacking if a.element_counts[e] >= 2]
    b_fills = [e for e in a.lacking if b.element_counts[e] >= 2]
    return {
        "a_fills_b": a_fills, "b_fills_a": b_fills,
        "mutual": bool(a_fills) and bool(b_fills),
        "any": bool(a_fills) or bool(b_fills),
    }


# 점수 표시: 원점수(raw)를 친화적 밴드로 재보정 + 티어 라벨.
# %는 측정값이 아니라 엔터테인먼트 지표 — 상대적 순서는 유지, 무서운 낮은 값은 배제.
def display_score(raw: int) -> int:
    raw = max(48, min(110, raw))
    return round(max(60, min(99, 74 + (raw - 48) / 62 * 24)))


_TIERS = [(90, "Soulmate Inyeon"), (84, "Harmony Match"), (78, "Growth Match")]


def tier(score: int) -> str:
    for th, label in _TIERS:
        if score >= th:
            return label
    return "Spark Match"   # 도전·끌림형 (파국 아님)


@dataclass
class Compatibility:
    score: int          # 표시 점수(재보정)
    raw: int            # 원점수 (이름 튜닝 계산용)
    tier: str
    day_master: dict
    zodiac: dict
    complement: dict
    headline_ko: str
    headline_en: str

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "tier": self.tier,
            "day_master": self.day_master,
            "zodiac": self.zodiac,
            "complement": {
                "a_fills_b": [e.en for e in self.complement["a_fills_b"]],
                "b_fills_a": [e.en for e in self.complement["b_fills_a"]],
                "mutual": self.complement["mutual"],
            },
            "headline_ko": self.headline_ko,
            "headline_en": self.headline_en,
        }


def compatibility(a: Chart, b: Chart) -> Compatibility:
    """두 사주 → 종합 궁합."""
    dm = day_master_relation(a.day_master, b.day_master)
    zo = zodiac_relation(a.zodiac, b.zodiac)
    comp = element_complement(a, b)

    raw = 50
    raw += {"상생": 25, "비화": 10, "상극": 6}[dm["type"]]
    raw += {"삼합": 20, "육합": 15, "무": 5, "충": -8}[zo["type"]]
    if comp["mutual"]:
        raw += 15
    elif comp["any"]:
        raw += 8
    score = display_score(raw)
    t = tier(score)

    en = f"{score}% · {t} — {dm['type_en']} Day Masters, {zo['type_en']} zodiac."
    ko = f"{score}% · {t} — 일간 {dm['type']}, 띠 {zo['type']}."
    if comp["mutual"]:
        en += " You fill each other's missing energy."
        ko += " 서로의 부족한 기운을 채워줌."
    return Compatibility(score, raw, t, dm, zo, comp, ko, en)

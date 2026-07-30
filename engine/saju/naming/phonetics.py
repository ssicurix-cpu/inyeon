"""
발음오행 — 한글 초성(첫 자음) → 오행. (결정론적, 정확히 계산 가능)

배속(현대 성명학 통용):
  ㄱ·ㅋ·ㄲ = 木(목)  | ㄴ·ㄷ·ㄹ·ㅌ·ㄸ = 火(화)
  ㅅ·ㅈ·ㅊ·ㅆ·ㅉ = 金(금) | ㅁ·ㅂ·ㅍ·ㅃ = 水(수) | ㅇ·ㅎ = 土(토)

**유파차 주의:** 훈민정음 원리에선 脣音(ㅁㅂㅍ)=土, 喉音(ㅇㅎ)=水 로 위와 반대다.
본 엔진은 현대 성명학 통용 배속을 기본값으로 하되, 향후 전문가 감수 시 확정.
"""
from __future__ import annotations

from ..core import Element

# 초성 19개 인덱스: ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ
_CHO_ELEMENT = {
    0: Element.WOOD, 1: Element.WOOD, 15: Element.WOOD,               # ㄱㄲㅋ
    2: Element.FIRE, 3: Element.FIRE, 4: Element.FIRE, 5: Element.FIRE, 16: Element.FIRE,  # ㄴㄷㄸㄹㅌ
    9: Element.METAL, 10: Element.METAL, 12: Element.METAL, 13: Element.METAL, 14: Element.METAL,  # ㅅㅆㅈㅉㅊ
    6: Element.WATER, 7: Element.WATER, 8: Element.WATER, 17: Element.WATER,  # ㅁㅂㅃㅍ
    11: Element.EARTH, 18: Element.EARTH,                              # ㅇㅎ
}


def sound_element(syllable: str) -> Element | None:
    """한글 음절 1글자 → 발음오행 (초성 기준). 한글 아니면 None."""
    code = ord(syllable[0])
    if not (0xAC00 <= code <= 0xD7A3):
        return None
    cho = (code - 0xAC00) // 588
    return _CHO_ELEMENT[cho]


def name_sound_elements(name: str) -> list[Element]:
    """한글 이름 → 음절별 발음오행 리스트."""
    out = []
    for ch in name:
        e = sound_element(ch)
        if e is not None:
            out.append(e)
    return out


# 외국 이름 첫소리 → 오행 (자음 소리 기준, 로마자 첫 글자 근사)
_LATIN_FIRST = {
    **{c: Element.WOOD for c in "gkcq"},
    **{c: Element.FIRE for c in "ndtlr"},
    **{c: Element.WATER for c in "mbpfvw"},
    **{c: Element.METAL for c in "szjx"},
    **{c: Element.EARTH for c in "aeiouhy"},
}


def foreign_first_element(name: str) -> Element | None:
    """외국 이름의 첫소리 오행 (음 유사 랭킹용)."""
    for ch in name.lower():
        if ch.isalpha():
            return _LATIN_FIRST.get(ch, Element.EARTH)
    return None

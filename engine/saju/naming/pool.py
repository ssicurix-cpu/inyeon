"""
검증된 이름 풀 (시드) + 성(姓) 표.

핵심 자산: 실제 현대 인기 given name들. 발음오행은 코드로 계산(정확),
한자·뜻은 '예시(감수 전)' — 실서비스는 대법원 인기 이름 통계 + 전문가 감수로 확장.
이름은 '생성'이 아니라 이 풀에서 '선별'한다(촌스러움 방지).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..core import Element
from .phonetics import name_sound_elements, sound_element


@dataclass
class NameEntry:
    hangul: str
    gender: str                 # "M" / "F" / "U"(유니섹스)
    hanja: str | None = None    # 예시(감수 전)
    meaning: str | None = None  # 예시(감수 전)
    sound_elements: list[Element] = field(default_factory=list)

    def __post_init__(self):
        if not self.sound_elements:
            self.sound_elements = name_sound_elements(self.hangul)

    def supplies(self, element: Element) -> bool:
        return element in self.sound_elements

    @property
    def first_element(self) -> Element:
        return self.sound_elements[0]


# 현대 인기 이름 시드 풀 (한자·뜻은 일부만 예시로 첨부)
SEED_NAMES: list[NameEntry] = [
    # 남 (M)
    NameEntry("도윤", "M", "道潤", "길 도 · 윤택할 윤 (path · flourishing)"),
    NameEntry("하준", "M"),
    NameEntry("서준", "M"),
    NameEntry("민준", "M", "敏俊", "민첩할 민 · 준수할 준 (quick · talented)"),
    NameEntry("건우", "M", "健宇", "굳셀 건 · 집 우 (strong · great)"),
    NameEntry("태오", "M"),
    NameEntry("지호", "M"),
    NameEntry("강민", "M"),
    NameEntry("준서", "M"),
    NameEntry("은우", "M"),
    # 여 (F)
    NameEntry("서연", "F", "瑞娟", "상서로울 서 · 아름다울 연 (auspicious · beautiful)"),
    NameEntry("지우", "F", "智宇", "지혜 지 · 집 우 (wisdom · universe)"),
    NameEntry("하은", "F"),
    NameEntry("다은", "F"),
    NameEntry("가은", "F"),
    NameEntry("민서", "F"),
    NameEntry("유진", "F"),
    NameEntry("수아", "F"),
    NameEntry("나윤", "F"),
    NameEntry("보라", "F"),
]

# 성(姓) 표: 발음오행은 코드로 계산. 인기순 근사 정렬.
_SURNAME_HANGUL = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
                   "한", "오", "서", "신", "문", "류", "노", "도"]


@dataclass
class Surname:
    hangul: str
    element: Element


SURNAMES: list[Surname] = [Surname(s, sound_element(s)) for s in _SURNAME_HANGUL]


def names_by_gender(gender: str) -> list[NameEntry]:
    return [n for n in SEED_NAMES if n.gender == gender or n.gender == "U"]


def surnames_supplying(element: Element) -> list[Surname]:
    return [s for s in SURNAMES if s.element is element]

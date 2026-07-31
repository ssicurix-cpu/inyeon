"""
검증된 이름 풀 (시드) + 성(姓) 표 + 인명용 한자 DB(한자·뜻·자원오행).

핵심 자산: 실제 현대 인기 given name들. 이름은 '생성'이 아니라 이 풀에서 '선별'(촌스러움 방지).
- 발음오행: 코드로 계산(정확).
- 한자·뜻: 인기 이름의 통용 한자·뜻 (공개 데이터 기반, v1).
- 자원오행: **부수(radical) 기반 통용 기준으로 모든 글자에 배정.** 자원오행은 단일 정답이 없는 유파 영역이라
  '공인된 하나'가 없음 → 널리 쓰이는 부수→오행 표를 **일관되게** 적용(정답이 아니라 일관성이 핵심).
  유료 상품이라 미배정(None) 없이 전부 채운다. ('certified' 과장 금지 = "traditional 오행 방식".)
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..core import Element
from .phonetics import name_sound_elements, sound_element

W, F_, T, G, S = Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER

# 인명용 한자 DB: char → (뜻(영문 짧게), 자원오행). 자원오행은 부수(radical) 기반 통용 기준으로 전부 배정.
# 부수→오행 통용 기준(요약): 氵水雨夕月→水 · 火日心彳辶亻→火 · 木禾竹广目→木 · 金玉貝攵→金 · 土山石田女力宀→土
HANJA: dict[str, tuple[str, Element]] = {
    # 水 (water)  氵·水·夕·月(肉)
    "潤": ("flourishing, moist", S), "河": ("river", S), "泰": ("great, calm", S),
    "洙": ("riverbank", S), "沿": ("along a stream", S), "浩": ("vast", S), "海": ("sea", S),
    "潾": ("clear water", S), "有": ("to have", S), "多": ("abundant", S),
    # 火 (fire / sun / heart / person / motion)  火·日·心·亻·彳·辶
    "智": ("wisdom", F_), "昊": ("vast sky", F_), "昭": ("bright", F_), "旿": ("bright noon", F_),
    "恩": ("grace", F_), "晛": ("sunlight", F_), "炫": ("shining", F_), "旻": ("autumn sky", F_),
    "道": ("path", F_), "俊": ("talented", F_), "健": ("strong", F_), "佳": ("fine, beautiful", F_),
    "書": ("book, writing", F_), "律": ("rhythm, law", F_),
    # 木 (wood / grain / eaves)  木·禾·竹·广·目
    "秀": ("excellent, elegant", W), "松": ("pine", W), "桓": ("strong tree", W),
    "彬": ("refined", W), "榮": ("glory, flourish", W), "柔": ("gentle", W),
    "康": ("peaceful, healthy", W), "睿": ("wise, insightful", W),
    # 金 (metal / jade / shell / strike)  金·玉·貝·攵
    "瑞": ("auspicious", G), "珍": ("treasure", G), "錫": ("bestow", G),
    "玟": ("gem", G), "瑀": ("jade", G), "珉": ("jade-like stone", G), "敏": ("quick, clever", G),
    # 土 (earth / mountain / woman / strength / roof)  土·山·女·力·宀
    "宇": ("house, cosmos", T), "圭": ("jade tablet", T), "城": ("fortress", T),
    "娟": ("beautiful", T), "娥": ("graceful", T), "垠": ("boundary, land", T),
    "娜": ("graceful", T), "勳": ("merit", T),
}


@dataclass
class NameEntry:
    hangul: str
    gender: str                 # "M" / "F" / "U"
    hanja: str | None = None
    meaning: str | None = None
    sound_elements: list[Element] = field(default_factory=list)
    resource_elements: list = field(default_factory=list)  # 자원오행(글자별), None 가능

    def __post_init__(self):
        if not self.sound_elements:
            self.sound_elements = name_sound_elements(self.hangul)
        if self.hanja and not self.resource_elements:
            self.resource_elements = [HANJA.get(ch, (None, None))[1] for ch in self.hanja]
        # 뜻 자동 조합 (없을 때, DB에 있으면)
        if self.hanja and not self.meaning:
            parts = [HANJA[ch][0] for ch in self.hanja if ch in HANJA]
            if len(parts) == len(self.hanja):
                self.meaning = " · ".join(parts)

    def supplies(self, element: Element) -> bool:
        """발음오행으로 해당 원소를 공급하는가 (매칭 하드필터)."""
        return element in self.sound_elements

    def resource_supplies(self, element: Element) -> bool:
        """자원오행으로 해당 원소를 공급하는가 (부가 신호)."""
        return element in [e for e in self.resource_elements if e]

    @property
    def first_element(self) -> Element:
        return self.sound_elements[0]

    @property
    def hanja_breakdown(self) -> list[dict]:
        """글자별 한자·뜻·자원오행 (이름 카드용)."""
        out = []
        for ch in (self.hanja or ""):
            m, el = HANJA.get(ch, (None, None))
            out.append({"char": ch, "meaning": m, "element": el})
        return out


# 현대 인기 이름 시드 풀 (한자·뜻·자원오행 v1)
SEED_NAMES: list[NameEntry] = [
    # 남 (M)
    NameEntry("도윤", "M", "道潤"),
    NameEntry("하준", "M", "河俊"),
    NameEntry("서준", "M", "瑞俊"),
    NameEntry("민준", "M", "敏俊"),
    NameEntry("건우", "M", "健宇"),
    NameEntry("태오", "M", "泰旿"),
    NameEntry("지호", "M", "智昊"),
    NameEntry("강민", "M", "康敏"),
    NameEntry("준서", "M", "俊書"),
    NameEntry("은우", "M", "恩宇"),
    NameEntry("지훈", "M", "智勳"),
    NameEntry("현우", "M", "炫宇"),
    # 여 (F)
    NameEntry("서연", "F", "瑞娟"),
    NameEntry("지우", "F", "智宇"),
    NameEntry("하은", "F", "河恩"),
    NameEntry("다은", "F", "多恩"),
    NameEntry("가은", "F", "佳恩"),
    NameEntry("민서", "F", "敏瑞"),
    NameEntry("유진", "F", "有珍"),
    NameEntry("수아", "F", "秀娥"),
    NameEntry("나윤", "F", "娜潤"),
    NameEntry("예린", "F", "睿潾"),
    NameEntry("소율", "F", "昭律"),
    NameEntry("지아", "F", "智娥"),
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

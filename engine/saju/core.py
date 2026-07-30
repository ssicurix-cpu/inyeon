"""
saju.core — 사주 계산 엔진의 정의 코어 (Slice 1-2)

여기 담긴 것:
  - 오행(Five Elements), 음양(Yin/Yang)
  - 천간 10 (Heavenly Stems) / 지지 12 (Earthly Branches) + 지장간
  - 60갑자 (sexagenary cycle) 유틸
  - 일주(Day Pillar) 계산: 양력일 → 60갑자

정확도 원칙: 이 파일의 표는 전부 '정의'라 논쟁의 여지가 없다(천간·지지 순서,
오행 배속, 지지 동물). 유일한 계산 로직인 일주(day pillar) 앵커는
독립 라이브러리(sxtwl)로 검증한 값이며 tests/test_core.py 로 고정한다.

영어권 서비스가 목적이므로 각 원소에 한국어 + 로마자 + 영어를 함께 둔다(현지화용).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class Element(Enum):
    """오행 (Five Elements)."""
    WOOD = ("목", "Wood")
    FIRE = ("화", "Fire")
    EARTH = ("토", "Earth")
    METAL = ("금", "Metal")
    WATER = ("수", "Water")

    def __init__(self, ko: str, en: str):
        self.ko = ko
        self.en = en


class YinYang(Enum):
    """음양."""
    YANG = ("양", "Yang")
    YIN = ("음", "Yin")

    def __init__(self, ko: str, en: str):
        self.ko = ko
        self.en = en


@dataclass(frozen=True)
class Stem:
    """천간 (Heavenly Stem)."""
    index: int          # 0=甲 .. 9=癸
    hanja: str
    ko: str             # 한글 음
    rom: str            # 로마자
    element: Element
    polarity: YinYang


@dataclass(frozen=True)
class Branch:
    """지지 (Earthly Branch)."""
    index: int          # 0=子 .. 11=亥
    hanja: str
    ko: str
    rom: str
    element: Element
    polarity: YinYang
    animal_ko: str      # 띠 (한국어)
    animal_en: str      # zodiac animal (영어)


# --- 천간 10 (甲乙丙丁戊己庚辛壬癸) -------------------------------------------
W, F, E, M, T = Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER
YA, YI = YinYang.YANG, YinYang.YIN

STEMS: tuple[Stem, ...] = (
    Stem(0, "甲", "갑", "gap", W, YA),
    Stem(1, "乙", "을", "eul", W, YI),
    Stem(2, "丙", "병", "byeong", F, YA),
    Stem(3, "丁", "정", "jeong", F, YI),
    Stem(4, "戊", "무", "mu", E, YA),
    Stem(5, "己", "기", "gi", E, YI),
    Stem(6, "庚", "경", "gyeong", M, YA),
    Stem(7, "辛", "신", "sin", M, YI),
    Stem(8, "壬", "임", "im", T, YA),
    Stem(9, "癸", "계", "gye", T, YI),
)

# --- 지지 12 (子丑寅卯辰巳午未申酉戌亥) --------------------------------------
BRANCHES: tuple[Branch, ...] = (
    Branch(0, "子", "자", "ja", T, YA, "쥐", "Rat"),
    Branch(1, "丑", "축", "chuk", E, YI, "소", "Ox"),
    Branch(2, "寅", "인", "in", W, YA, "호랑이", "Tiger"),
    Branch(3, "卯", "묘", "myo", W, YI, "토끼", "Rabbit"),
    Branch(4, "辰", "진", "jin", E, YA, "용", "Dragon"),
    Branch(5, "巳", "사", "sa", F, YI, "뱀", "Snake"),
    Branch(6, "午", "오", "o", F, YA, "말", "Horse"),
    Branch(7, "未", "미", "mi", E, YI, "양", "Goat"),
    Branch(8, "申", "신", "sin", M, YA, "원숭이", "Monkey"),
    Branch(9, "酉", "유", "yu", M, YI, "닭", "Rooster"),
    Branch(10, "戌", "술", "sul", E, YA, "개", "Dog"),
    Branch(11, "亥", "해", "hae", T, YI, "돼지", "Pig"),
)

# --- 지장간 (hidden stems in each branch) — 여기/중기/정기, 정기가 마지막 ------
# 이후 오행 분포·십신 계산에 사용. stem index 리스트로 보관.
HIDDEN_STEMS: dict[int, tuple[int, ...]] = {
    0:  (8, 9),          # 子: 壬 癸
    1:  (9, 7, 5),       # 丑: 癸 辛 己
    2:  (4, 2, 0),       # 寅: 戊 丙 甲
    3:  (0, 1),          # 卯: 甲 乙
    4:  (1, 9, 4),       # 辰: 乙 癸 戊
    5:  (4, 6, 2),       # 巳: 戊 庚 丙
    6:  (2, 5, 3),       # 午: 丙 己 丁
    7:  (3, 1, 5),       # 未: 丁 乙 己
    8:  (4, 8, 6),       # 申: 戊 壬 庚
    9:  (6, 7),          # 酉: 庚 辛
    10: (7, 3, 4),       # 戌: 辛 丁 戊
    11: (4, 0, 8),       # 亥: 戊 甲 壬
}


@dataclass(frozen=True)
class GanZhi:
    """간지 한 기둥 (천간 + 지지). sexagenary_index: 0=甲子 .. 59=癸亥."""
    stem: Stem
    branch: Branch

    @property
    def sexagenary_index(self) -> int:
        # 60갑자에서 stem은 10주기, branch는 12주기로 동시에 도는 값 → CRT로 복원.
        # idx%10==stem, idx%12==branch 를 만족하는 0..59 유일값.
        for i in range(60):
            if i % 10 == self.stem.index and i % 12 == self.branch.index:
                return i
        raise ValueError("invalid stem/branch combination")

    @property
    def hanja(self) -> str:
        return self.stem.hanja + self.branch.hanja

    @property
    def ko(self) -> str:
        return self.stem.ko + self.branch.ko

    def __str__(self) -> str:
        return self.hanja


def ganzhi_from_index(i: int) -> GanZhi:
    """0..59 sexagenary index → GanZhi."""
    i %= 60
    return GanZhi(STEMS[i % 10], BRANCHES[i % 12])


# --- 일주(Day Pillar) --------------------------------------------------------
# 60갑자 일주는 날짜만의 함수(연속 순환). 검증: 아래 offset은 sxtwl(寿星天文历)
# 기준 5개 날짜에서 일치 확인 (tests/test_core.py). 甲子(0)로 떨어지는 앵커.
_DAY_PILLAR_OFFSET = 14  # (date.toordinal() + 14) % 60 == sexagenary index


def day_pillar(d: date) -> GanZhi:
    """양력 날짜 → 일주 간지. (진태양시로 인한 날짜 경계 보정은 상위 단계에서 처리)"""
    return ganzhi_from_index((d.toordinal() + _DAY_PILLAR_OFFSET) % 60)

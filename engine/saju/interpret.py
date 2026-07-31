"""
saju.interpret — 경량 해석 레이어 (Slice: 무료 훅용)

두 축:
  1. 불변 콘텐츠(build_facts) — 계산값을 "Your Missing Element" 렌즈로 의미화.
     강점 먼저 → 없는 원소 = 성장의 열쇠 (건설적·비파국). 페르소나 무관 고정.
  2. 페르소나 말투(Persona) — 같은 사실을 3종 톤으로 렌더. 따뜻/직설/신비.

가드레일: 페르소나는 말투만 바꾼다. 사실·웰빙·비파국 규칙은 불변.
직설도 "넌 안 돼"가 아니라 "그러니 이걸 해"로.

프로토타입은 템플릿 기반(API 키 불필요). 실서비스는 이 사실 + 페르소나 지침을
LLM에 넘겨 자연스러운 문장으로 렌더(서버리스 함수).
"""
from __future__ import annotations

from enum import Enum

from .core import Element
from .chart import Chart

# 일간 = 자연 캐릭터 (실제 명리학 근거, 프레이밍만 우리 렌즈)
NATURE: dict[str, tuple[str, str]] = {
    "甲": ("a towering tree", "upright, ambitious and principled"),
    "乙": ("a climbing vine", "adaptable, gentle and quietly persistent"),
    "丙": ("the sun", "radiant, bold and impossible to ignore"),
    "丁": ("a candle flame", "warm, intimate and refined"),
    "戊": ("a mountain", "steady, dependable and protective"),
    "己": ("garden soil", "nurturing, practical and grounding for others"),
    "庚": ("a blade", "decisive, strong and unbreakable once set"),
    "辛": ("a polished gem", "refined, elegant and sharp-eyed for quality"),
    "壬": ("the open sea", "expansive, resourceful and always moving"),
    "癸": ("gentle rain", "intuitive, quiet and nourishing"),
}

# 원소별 테마: (강점 표현, 없을 때 찾아야 할 것)
ELEMENT_THEME: dict[Element, tuple[str, str]] = {
    Element.WOOD: ("growth, vision and patience", "putting down roots and letting things grow"),
    Element.FIRE: ("warmth, passion and presence", "letting yourself shine and connect"),
    Element.EARTH: ("grounding, stability and trust", "slowing down to build something solid"),
    Element.METAL: ("clarity, structure and resolve", "setting boundaries and cutting what drains you"),
    Element.WATER: ("flow, intuition and emotional depth", "learning to soften, rest and trust your gut"),
}


class Persona(Enum):
    WARM = ("The Warm Guide", "따뜻한 위로형")
    BLUNT = ("The Straight Talker", "직설 팩폭형")
    MYSTIC = ("The Mystic", "신비로운 무당형")

    def __init__(self, en: str, ko: str):
        self.label_en = en
        self.label_ko = ko


def build_facts(chart: Chart) -> dict:
    """계산값 → 해석 사실(불변). 페르소나 무관."""
    dm = chart.day_master
    nature, traits = NATURE[dm.hanja]
    missing = chart.lacking[0] if chart.lacking else None
    return {
        "polarity": dm.polarity.en,
        "element": dm.element.en,
        "nature": nature,
        "traits": traits,
        "dominant": chart.dominant,
        "dominant_strength": ELEMENT_THEME[chart.dominant][0],
        "missing": missing,
        "missing_theme": ELEMENT_THEME[missing][1] if missing else None,
    }


# --- 페르소나별 솔로 리딩 (무료 훅) ------------------------------------------

def _cap(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def _solo_warm(f: dict) -> str:
    # 친구가 보내는 다정한 문자체 (therapy-adjacent, 간결·2인칭)
    s = (f"You're {f['polarity']} {f['element']} — {f['nature']}. "
         f"Underneath it all, you're {f['traits']}. "
         f"That {f['dominant'].en} in you is real — {f['dominant_strength']} come easy to you.")
    if f["missing"]:
        s += (f" But here's the tender part: you're missing {f['missing'].en}. "
              f"Not a flaw — it's what you're still growing toward. "
              f"{_cap(f['missing_theme'])} is where you'll finally feel whole. I've got you. 🤍")
    else:
        s += " And your five elements are beautifully balanced — a rare, adaptable heart."
    return s


def _solo_blunt(f: dict) -> str:
    # 애정 어린 로스트 — 다그치되 '간파당한' 느낌 + 위트 (악의 X)
    s = (f"Okay — {f['polarity']} {f['element']}, {f['nature']}. "
         f"You're {f['traits']}, and let's be real, you already know it. "
         f"{f['dominant'].en}? You've got it in spades — never your problem.")
    if f["missing"]:
        s += (f" Your problem? Zero {f['missing'].en} — the thing you keep dodging. "
              f"I see you. Start {f['missing_theme']}, and watch what happens. You're welcome. 😌")
    else:
        s += " And your elements are balanced, so stop overthinking and use it."
    return s


def _solo_mystic(f: dict) -> str:
    # WitchTok 톤 — 미스터리 + 임파워먼트/매니페스트 (아직 안 꺼낸 네 힘)
    s = (f"The chart doesn't lie: you're {f['polarity']} {f['element']} — {f['nature']}, "
         f"{f['traits']} to the core. "
         f"{f['dominant'].en} runs thick in you — {f['dominant_strength']} are yours.")
    if f["missing"]:
        s += (f" But one force stays quiet: {f['missing'].en}. "
              f"This isn't a gap in you — it's the power you haven't claimed yet. "
              f"Call in {f['missing_theme']}, and it becomes your magic. ✨")
    else:
        s += " And rare it is — all five forces already move as one in you."
    return s


_SOLO = {Persona.WARM: _solo_warm, Persona.BLUNT: _solo_blunt, Persona.MYSTIC: _solo_mystic}


def render_reading(chart: Chart, persona: Persona = Persona.WARM) -> str:
    """무료 훅 솔로 리딩 (선택한 페르소나 말투)."""
    return _SOLO[persona](build_facts(chart))


# --- 궁합 리딩 (간판 훅) — 강점 먼저·건설적·비파국 -----------------------------

def build_compat_facts(a: Chart, b: Chart) -> dict:
    from .compat import compatibility
    c = compatibility(a, b)
    return {
        "score": c.score, "rel": c.day_master["type"],
        "ea": a.day_master.element.en, "eb": b.day_master.element.en,
        "mutual": c.complement["mutual"],
        "zodiac_type": c.zodiac["type"],
        "a_animal": a.zodiac.animal_en, "b_animal": b.zodiac.animal_en,
    }


def _compat_strength(f: dict) -> str:
    if f["rel"] == "상생":
        return f"your {f['ea']} and their {f['eb']} feed each other — naturally supportive"
    if f["rel"] == "비화":
        return f"you're both {f['ea']} — cut from similar cloth, instantly familiar"
    return f"your {f['ea']} and their {f['eb']} create real spark — magnetic energy"


def _compat_challenge(f: dict) -> str | None:
    if f["rel"] == "상극":
        return "there's real friction here — but that tension is chemistry, not a wall"
    if f["zodiac_type"] == "충":
        return f"your {f['a_animal']} and their {f['b_animal']} clash — intense, never boring"
    return None


def _name_teaser(name_rec: dict | None) -> str | None:
    if not name_rec or not name_rec.get("best"):
        return None
    top = name_rec.get("both_boosted", name_rec.get("boosted_score"))
    return (f"a pair of Korean names — each carrying what the other lacks — "
            f"could tune your harmony from {name_rec['base_score']}% to {top}%")


def render_compat(a: Chart, b: Chart, persona: Persona = Persona.WARM,
                  name_rec: dict | None = None) -> str:
    f = build_compat_facts(a, b)
    strength, challenge, teaser = _compat_strength(f), _compat_challenge(f), _name_teaser(name_rec)
    if f["mutual"]:
        strength += ", and you literally fill each other's missing energy"

    if persona is Persona.WARM:
        s = f"You two are a {f['score']}% match. {_cap(strength)}. "
        if challenge:
            s += f"Honestly? {_cap(challenge)}. But that's workable — just be gentle with it. "
        if teaser:
            s += f"And if you want to nurture it, {teaser}. 🤍"
    elif persona is Persona.BLUNT:
        s = f"{f['score']}%. Real talk — {strength}. "
        if challenge:
            s += f"It's not all smooth: {challenge}. So actually deal with it. "
        if teaser:
            s += f"Want the cheat code? {_cap(teaser)}. 😌"
    else:  # MYSTIC
        s = f"The pillars entwine at {f['score']}%. {_cap(strength)}. "
        if challenge:
            s += f"The tension? That's the magic — {challenge}. "
        if teaser:
            s += f"And hear this: {teaser}. ✨"
    return s.strip()

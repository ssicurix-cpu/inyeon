"""
이름 생성 — 프리미엄 작명(A) + Koreanize(E).

공통 원칙: **부족 오행 보완 = 하드 필터, 원래 이름 유사도 = 랭킹, 선별은 검증된 풀에서.**
"""
from __future__ import annotations

from ..core import Element
from ..chart import Chart
from ..analysis import generates, controls
from ..compat import compatibility, day_master_relation, display_score, tier
from .phonetics import foreign_first_element
from .pool import NameEntry, names_by_gender, surnames_supplying, SURNAMES

# 이름 오행 레이어가 궁합에 더하는 보너스(원점수 기준, 재보정 전). 티어를 넘길 만큼.
_NAME_HARMONY_BONUS = 14


def target_element(chart: Chart) -> Element:
    """보완할 오행 = 부족(0개) 우선, 없으면 최소 개수 오행."""
    if chart.lacking:
        return chart.lacking[0]
    return min(chart.element_counts, key=lambda e: chart.element_counts[e])


def premium_korean_name(chart: Chart, gender: str, original_name: str,
                        top: int = 3) -> dict:
    """프리미엄 작명: 원래 이름 기반 + 부족 오행 보완, 검증된 풀에서 선별."""
    target = target_element(chart)
    orig_el = foreign_first_element(original_name)

    # 하드 필터: 부족 오행을 발음오행으로 공급하는 이름 + 성별
    candidates = [n for n in names_by_gender(gender) if n.supplies(target)]
    # 랭킹: 첫 음절 발음오행이 원래 이름 첫소리와 같으면 우선
    candidates.sort(key=lambda n: (n.first_element is not orig_el,))

    picks = candidates[:top]
    best = picks[0] if picks else None
    card = None
    if best:
        card = {
            "hangul": best.hangul,
            "hanja": best.hanja,
            "meaning": best.meaning,
            "breakdown": [  # 글자별 한자·뜻·자원오행 (유료 풀 네임 카드)
                {"char": b["char"], "meaning": b["meaning"],
                 "element": b["element"].en if b["element"] else None}
                for b in best.hanja_breakdown
            ],
            "sound_elements": [e.en for e in best.sound_elements],
            "target_element": target.en,
            "reasoning_en": _reason_en(best, target, original_name),
        }
    return {
        "target_element": target,
        "original_name": original_name,
        "candidates": picks,
        "best": best,
        "card": card,
        "reasoning": _reason(best, target, original_name) if best else None,
    }


def _reason_en(name: NameEntry, target: Element, original: str) -> str:
    s = (f"Inspired by the sound of “{original}”, we chose a name that pours in "
         f"{target.en} — the element your chart lacks.")
    if name.hanja:
        s += f" In hanja {name.hanja} means “{name.meaning}”."
    s += " Crafted the traditional 오행 way (for self-discovery, not fixed fate)."
    return s


def _reason(name: NameEntry, target: Element, original: str) -> str:
    base = (f"'{original}'의 첫소리를 잇고, 네 사주에 부족한 "
            f"{target.en}({target.ko})의 기운을 이름 소리에 채웠어.")
    if name.hanja:
        base += f" 한자 {name.hanja} — {name.meaning}."
    else:
        base += " (한자·뜻은 전문가 감수 후 확정)"
    return base


def harmonizing_element(self_chart: Chart, partner_chart: Chart) -> Element:
    """두 사람의 조화를 높이는 오행 (이름으로 보완할 대상).

    상극이면 通關(중재) 오행 — 두 일간 오행 사이를 잇는 것(火극金이면 土).
    상생/비화면 둘이 함께 가장 약한 오행.
    """
    ea = self_chart.day_master.element
    eb = partner_chart.day_master.element
    if day_master_relation(self_chart.day_master, partner_chart.day_master)["type"] == "상극":
        # ea가 eb를 극하면 generates(ea)가 통관, 반대면 generates(eb)
        return generates(ea) if controls(ea) is eb else generates(eb)
    joint = {e: self_chart.element_counts[e] + partner_chart.element_counts[e]
             for e in Element}
    return min(joint, key=lambda e: joint[e])


def name_to_improve_compat(self_chart: Chart, partner_chart: Chart, gender: str,
                           original_name: str | None = None, top: int = 3) -> dict:
    """상대에 맞춰 둘의 조화를 높이는 한국 이름 추천 (핵심 결제 전환).

    정직 한계: 일간·띠(출생 고정)는 이름으로 못 바꿈. 이름은 '이름 오행 레이어'만 조정.
    """
    base = compatibility(self_chart, partner_chart)
    target = harmonizing_element(self_chart, partner_chart)

    candidates = [n for n in names_by_gender(gender) if n.supplies(target)]
    if original_name:
        orig_el = foreign_first_element(original_name)
        candidates.sort(key=lambda n: (n.first_element is not orig_el,))

    best = candidates[0] if candidates else None
    boosted = display_score(base.raw + _NAME_HARMONY_BONUS) if best else base.score
    # 둘 다 이름을 튜닝하면(파트너까지) 조화 레이어가 한 번 더 쌓임 → 두 번째 사람 유입 훅
    both = display_score(base.raw + 2 * _NAME_HARMONY_BONUS) if best else base.score

    rel = base.day_master["type"]
    if best:
        ko = (f"둘은 {rel} 관계. {target.ko}의 기운을 이름에 넣으면 조화가 붙어. "
              f"'{best.hangul}'가 {target.en}을 더해 → 궁합 {base.score}% → {boosted}%. "
              f"(운명을 바꾸는 게 아니라 '이름 오행 레이어'를 튜닝)")
        en = (f"You two are '{rel}'. A name carrying {target.en} energy adds harmony. "
              f"'{best.hangul}' brings {target.en} → compatibility {base.score}% → {boosted}%. "
              f"(tunes the name-element layer, not your fate)")
    else:
        ko = en = None
    return {
        "base_score": base.score,
        "boosted_score": boosted,
        "both_boosted": both,
        "both_tier": tier(both),
        "harmonizing_element": target,
        "relation_type": rel,
        "best": best,
        "candidates": candidates[:top],
        "reasoning_ko": ko,
        "reasoning_en": en,
    }


def couple_names(self_chart: Chart, partner_chart: Chart, self_gender: str,
                 partner_gender: str, self_name: str | None = None,
                 partner_name: str | None = None, top: int = 3) -> dict:
    """둘만의 인연 이름: 각자 이름이 '상대가 부족한 오행'을 담아 서로를 채운다.

    컨셉 — 개명이 아니라 '둘만의 애칭'. 서로를 부르면 상대의 없는 기운을 소리로
    채워줌 → 이름 오행/조화 레이어가 튜닝됨. 정직: 일간·띠는 못 바꿈, 조화 레이어만.
    """
    base = compatibility(self_chart, partner_chart)
    self_target = target_element(partner_chart)   # 내 이름 = 상대의 부족 오행
    partner_target = target_element(self_chart)    # 상대 이름 = 나의 부족 오행

    def _pick(gender: str, target: Element, orig: str | None):
        cands = [n for n in names_by_gender(gender) if n.supplies(target)]
        if orig:
            oe = foreign_first_element(orig)
            cands.sort(key=lambda n: (n.first_element is not oe,))
        return (cands[0] if cands else None), cands[:top]

    self_best, self_cands = _pick(self_gender, self_target, self_name)
    partner_best, partner_cands = _pick(partner_gender, partner_target, partner_name)

    both_ok = bool(self_best and partner_best)
    both = display_score(base.raw + 2 * _NAME_HARMONY_BONUS) if both_ok else base.score

    def _card(best, cands, target, for_whom):
        if not best:
            return None
        d = {"hangul": best.hangul, "hanja": best.hanja, "meaning": best.meaning,
             "target_element": target, "candidates": [c.hangul for c in cands]}
        d["blurb_en"] = (f"{best.hangul} carries {target.en} — the element "
                         f"{for_whom} is missing.")
        return d

    return {
        "base_score": base.score,
        "both_boosted": both,
        "both_tier": tier(both),
        "self_card": _card(self_best, self_cands, self_target, "your partner"),
        "partner_card": _card(partner_best, partner_cands, partner_target, "you"),
    }


def koreanize(given_name: str, chart: Chart, top: int = 3) -> dict:
    """무료 유입: 이름은 그대로 두고 사주 매칭 한국 성만 붙임 (예: 김 Taylor)."""
    target = target_element(chart)
    matched = surnames_supplying(target)
    fallback = SURNAMES  # 매칭 성 없을 때
    surs = matched if matched else fallback
    options = [f"{s.hangul} {given_name}" for s in surs[:top]]
    return {
        "target_element": target,
        "given_name": given_name,
        "options": options,
        "reasoning": (f"네 사주에 부족한 {target.en}({target.ko}) 기운을 가진 "
                      f"한국 성을 붙였어 (발음오행 매칭). "
                      f'"your name with a Korean surname" — 재미용.'),
    }

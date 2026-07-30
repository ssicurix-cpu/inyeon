"""핵심 결제 전환 데모 — 궁합 → '이 이름이 조화를 높인다'."""
from datetime import datetime

from saju.place import chart_for_city
from saju.compat import compatibility
from saju.naming import name_to_improve_compat

# Emma(火) × Jihoon(金) — 상극(끌림+긴장)
emma = chart_for_city(datetime(1990, 6, 21, 14, 30), "New York")
jihoon = chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")

base = compatibility(emma, jihoon)
print("=== Emma × Jihoon ===")
print(f"Emma: 일간 {emma.day_master.element.en} / Jihoon: 일간 {jihoon.day_master.element.en}")
print(f"\n[무료 궁합] {base.headline_en}")
print(f"  · {base.day_master['en']}")

# 프리미엄 전환: Emma의 이름을 상대 맞춤으로
rec = name_to_improve_compat(emma, jihoon, gender="F", original_name="Emma")
print(f"\n[프리미엄 — 상대 맞춤 이름]")
print(f"  통관 오행: {rec['harmonizing_element'].en} (火극金 사이를 잇는 土)")
print(f"  추천 이름: {rec['best'].hangul}"
      + (f" ({rec['best'].hanja})" if rec['best'].hanja else ""))
print(f"  궁합: {rec['base_score']}% → {rec['boosted_score']}%")
print(f"  {rec['reasoning_en']}")
others = ", ".join(n.hangul for n in rec["candidates"][1:])
if others:
    print(f"  다른 후보: {others}")

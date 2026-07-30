"""해석 레이어 샘플 — 같은 사실, 3가지 무당 말투."""
from datetime import datetime

from saju.place import chart_for_city
from saju.interpret import Persona, render_reading, render_compat
from saju.naming import name_to_improve_compat

jihoon = chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")
emma = chart_for_city(datetime(1990, 6, 21, 14, 30), "New York")

print("╔══ 솔로 리딩 — Jihoon (庚 Metal, 물 부족) ══╗")
print("   같은 계산, 페르소나 말투만 다름\n")
for p in Persona:
    print(f"─── {p.label_en} ({p.label_ko}) ───")
    print(render_reading(jihoon, p))
    print()

print("\n╔══ 궁합 리딩 — Emma × Jihoon (상극·통관 이름 처방) ══╗\n")
rec = name_to_improve_compat(emma, jihoon, gender="F", original_name="Emma")
for p in Persona:
    print(f"─── {p.label_en} ({p.label_ko}) ───")
    print(render_compat(emma, jihoon, p, name_rec=rec))
    print()

"""궁합 데모 — 간판 훅. 두 사람 사주 → 궁합 스토리."""
from datetime import datetime

from saju.place import chart_for_city
from saju.compat import compatibility


def pair(name_a, dt_a, city_a, name_b, dt_b, city_b):
    a = chart_for_city(dt_a, city_a)
    b = chart_for_city(dt_b, city_b)
    c = compatibility(a, b)
    print(f"\n=== {name_a} × {name_b} ===")
    print(f"{name_a}: {a.eight_char()} (일간 {a.day_master.element.en}, {a.zodiac.animal_en})")
    print(f"{name_b}: {b.eight_char()} (일간 {b.day_master.element.en}, {b.zodiac.animal_en})")
    print(f"\n  ★ Compatibility: {c.score}%")
    print(f"  · Day Master: {c.day_master['en']}")
    print(f"  · Zodiac: {c.zodiac['en']}")
    if c.complement["a_fills_b"] or c.complement["b_fills_a"]:
        af = [e.en for e in c.complement['a_fills_b']]
        bf = [e.en for e in c.complement['b_fills_a']]
        print(f"  · Element complement: {name_a}→{name_b} {af}, {name_b}→{name_a} {bf}")
    print(f"  → {c.headline_en}")


# 상극 케이스 (Emma 火 × 지훈 金)
pair("Emma", datetime(1990, 6, 21, 14, 30), "New York",
     "Jihoon", datetime(1990, 5, 15, 6, 30), "Seoul")

# 상생 + 상호보완 케이스 (지훈 金 × Oliver 水)
pair("Jihoon", datetime(1990, 5, 15, 6, 30), "Seoul",
     "Oliver", datetime(1985, 12, 10, 9, 0), "London")

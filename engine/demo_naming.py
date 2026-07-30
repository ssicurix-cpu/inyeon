"""이름 작명 데모 — 외국인 사주로 프리미엄 작명 + Koreanize."""
from datetime import datetime

from saju.place import chart_for_city
from saju.naming import premium_korean_name, koreanize


def show(person, local_dt, city, gender, given):
    c = chart_for_city(local_dt, city)
    lack = [e.en for e in c.lacking]
    print(f"\n=== {person} ({given}) — {city} ===")
    print(f"사주 {c.eight_char()} | 일간 {c.day_master.element.en} | 부족 오행: {lack}")

    pr = premium_korean_name(c, gender=gender, original_name=given)
    best = pr["best"]
    print(f"[프리미엄] Your Korean name: {best.hangul}"
          + (f" ({best.hanja})" if best.hanja else ""))
    print(f"          {pr['reasoning']}")
    others = ", ".join(n.hangul for n in pr["candidates"][1:])
    if others:
        print(f"          다른 후보: {others}")

    kz = koreanize(given, c)
    print(f"[무료 Koreanize] {'  '.join(kz['options'])}")
    print(f"          {kz['reasoning']}")


# 뉴욕(木 부족), 런던(金 부족), 서울(水 부족)
show("Emma", datetime(1990, 6, 21, 14, 30), "New York", "F", "Emma")
show("Oliver", datetime(1985, 12, 10, 9, 0), "London", "M", "Oliver")
show("지훈", datetime(1990, 5, 15, 6, 30), "Seoul", "M", "Jihoon")

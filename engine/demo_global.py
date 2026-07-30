"""외국인 사용자 데모 — 도시만 고르면 DST까지 자동 해석."""
from datetime import datetime

from saju.place import chart_for_city


def show(name, local_dt, city):
    c = chart_for_city(local_dt, city)
    print(f"\n=== {name} — {city}, {local_dt:%Y-%m-%d %H:%M} ===")
    print(f"진태양시(경도+DST+균시차 보정): {c.true_solar_time:%Y-%m-%d %H:%M}")
    print(f"사주팔자(Four Pillars): {c.eight_char()}")
    print(f"일간(Day Master): {c.day_master.hanja} = {c.day_master.element.en} "
          f"({c.day_master.polarity.en})")
    dist = "  ".join(f"{e.en}:{n}" for e, n in c.element_counts.items())
    print(f"오행(Five Elements): {dist}")
    print(f"  부족(작명 보완 대상): {[e.en for e in c.lacking]} | 최다: {c.dominant.en}")
    # 가입 유인 훅
    print(f"[가입 시 제공] Your lunar birthday: {c.lunar}  |  "
          f"Korean zodiac: {c.zodiac.animal_en} ({c.zodiac.animal_ko})")


# 미국인 (여름 출생 → EDT 자동 적용)
show("Emma (American)", datetime(1990, 6, 21, 14, 30), "New York")
# 영국인 (겨울 출생 → GMT)
show("Oliver (British)", datetime(1985, 12, 10, 9, 0), "London")
# 비교용 한국
show("지훈 (Korean)", datetime(1990, 5, 15, 6, 30), "Seoul")

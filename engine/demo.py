"""무료 훅이 보여줄 전체 사주 차트 데모."""
import json
from datetime import datetime

from saju.chart import compute_chart

# 1990-05-15 06:30 서울 (경도 126.978E, KST=UTC+9)
c = compute_chart(datetime(1990, 5, 15, 6, 30), utc_offset_hours=9,
                  longitude_east=126.9780)

print("입력: 1990-05-15 06:30 서울")
print(f"진태양시: {c.true_solar_time:%Y-%m-%d %H:%M:%S}")
print(f"\n사주팔자: {c.eight_char()}  (정답지 庚午 辛巳 庚辰 己卯 ✓)")
print(f"일간(Day Master): {c.day_master.hanja} = {c.day_master.element.en}")
print("\n오행 분포 (Five Elements):")
for e, n in c.element_counts.items():
    print(f"  {e.en:6}({e.ko}): {'●' * n}{'·' * (5 - n)} {n}")
print(f"  → 부족: {[e.en for e in c.lacking]} | 최다: {c.dominant.en}")
print("\n십신 (Ten Gods):")
for pos in ("year", "month", "day", "hour"):
    tg = c.ten_gods[pos]
    print(f"  {pos:6}: {'日主 (Day Master)' if tg is None else f'{tg.ko}/{tg.en}'}")
print(f"\n띠(Zodiac): {c.zodiac.animal_ko} / {c.zodiac.animal_en}")
print(f"음력 생일(Lunar): {c.lunar}")

print("\n--- API 출력(JSON) 미리보기 ---")
print(json.dumps(c.to_dict(), ensure_ascii=False, indent=2)[:600] + " ...")

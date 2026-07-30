"""
글로벌 시간대·DST 해석 + 외국인 케이스 검증.

DST 해석: 뉴욕 여름=EDT(-4)/겨울=EST(-5), 런던 겨울=GMT(0)/여름=BST(+1).

외국인 정답지 — New York, 1990-06-21 14:30 (EDT):
  UTC 18:30, 진태양시 ≈ 13:32(未시)
  사주 庚午 壬午 丁巳 丁未 (연/일 sxtwl, 월/시 규칙 검증)
  일간 丁(火), 오행 火5(과다)·木0(부족), 말띠, 음력 1990-05-29
"""
from datetime import datetime

from saju.core import Element
from saju.place import utc_offset_hours, chart_for_place, chart_for_city


# --- 역사적 DST 해석 ---------------------------------------------------------

def test_dst_offsets():
    assert utc_offset_hours(datetime(1990, 6, 21, 12), "America/New_York") == -4   # EDT
    assert utc_offset_hours(datetime(1990, 1, 15, 12), "America/New_York") == -5   # EST
    assert utc_offset_hours(datetime(1985, 12, 10, 9), "Europe/London") == 0       # GMT
    assert utc_offset_hours(datetime(1985, 6, 10, 9), "Europe/London") == 1        # BST


# --- 외국인 전체 차트 (뉴욕) -------------------------------------------------

def test_newyork_foreigner_chart():
    c = chart_for_city(datetime(1990, 6, 21, 14, 30), "New York")
    assert c.eight_char() == "庚午 壬午 丁巳 丁未"
    assert c.day_master.hanja == "丁"
    assert c.day_master.element is Element.FIRE
    # 진태양시 未시(13~15)
    assert c.true_solar_time.hour == 13
    # 오행: 火 과다, 木 부족
    assert c.element_counts[Element.FIRE] == 5
    assert c.element_counts[Element.WOOD] == 0
    assert c.lacking == [Element.WOOD]
    assert c.dominant is Element.FIRE
    # 띠 / 음력
    assert c.zodiac.animal_en == "Horse"
    assert (c.lunar.year, c.lunar.month, c.lunar.day) == (1990, 5, 29)


def test_seoul_via_place_matches_offset9():
    # 서울은 DST 없음 → 오프셋 항상 +9
    assert utc_offset_hours(datetime(1990, 5, 15, 6, 30), "Asia/Seoul") == 9
    c = chart_for_city(datetime(1990, 5, 15, 6, 30), "Seoul")
    assert c.eight_char() == "庚午 辛巳 庚辰 己卯"


def test_dst_boundary_affects_pillars():
    # 같은 벽시계라도 DST 유무로 UTC가 1시간 달라짐(뉴욕 여름 vs 겨울 오프셋)
    summer = utc_offset_hours(datetime(1990, 7, 1, 12), "America/New_York")
    winter = utc_offset_hours(datetime(1990, 12, 1, 12), "America/New_York")
    assert summer - winter == 1

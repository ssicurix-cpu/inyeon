"""
오행 분포·십신·음력·전체 차트 검증.

표준 케이스 1990-05-15 06:30 서울:
  사주 庚午 辛巳 庚辰 己卯
  오행 분포 金3 土2 火2 木1 水0 (水 없음)
  십신 년=비견 월=겁재 시=정인 (lunar_python 정답지)
  음력 1990-04-21, 말띠
"""
from datetime import datetime, date

from saju.core import Element, STEMS
from saju.analysis import ten_god, TenGod, element_counts, lacking_elements, dominant_element
from saju.lunar import to_lunar
from saju.chart import compute_chart

SEOUL_LON = 126.9780


def test_ten_god_main_case():
    gyeong = STEMS[6]  # 庚 (일간)
    assert ten_god(gyeong, STEMS[6]) is TenGod.BIGYEON     # 庚 년간 → 비견
    assert ten_god(gyeong, STEMS[7]) is TenGod.GEOMJAE     # 辛 월간 → 겁재
    assert ten_god(gyeong, STEMS[5]) is TenGod.JEONGIN     # 己 시간 → 정인


def test_lunar_main_case():
    ld = to_lunar(date(1990, 5, 15))
    assert (ld.year, ld.month, ld.day) == (1990, 4, 21)
    assert ld.is_leap_month is False


def test_full_chart_main_case():
    c = compute_chart(datetime(1990, 5, 15, 6, 30), utc_offset_hours=9,
                      longitude_east=SEOUL_LON)
    assert c.eight_char() == "庚午 辛巳 庚辰 己卯"
    assert c.day_master.hanja == "庚"
    assert c.day_master.element is Element.METAL
    # 오행 분포
    assert c.element_counts[Element.METAL] == 3
    assert c.element_counts[Element.EARTH] == 2
    assert c.element_counts[Element.FIRE] == 2
    assert c.element_counts[Element.WOOD] == 1
    assert c.element_counts[Element.WATER] == 0
    assert c.lacking == [Element.WATER]
    assert c.dominant is Element.METAL
    # 띠 / 음력
    assert c.zodiac.animal_en == "Horse"
    assert (c.lunar.year, c.lunar.month, c.lunar.day) == (1990, 4, 21)


def test_element_counts_sum_is_eight():
    c = compute_chart(datetime(1990, 5, 15, 6, 30), 9, SEOUL_LON)
    assert sum(c.element_counts.values()) == 8


def test_chart_to_dict_serializable():
    import json
    c = compute_chart(datetime(1990, 5, 15, 6, 30), 9, SEOUL_LON)
    s = json.dumps(c.to_dict(), ensure_ascii=False)
    assert "庚午" in s and "Horse" in s and "Metal" in s

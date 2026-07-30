"""
saju.place — 출생지 → 시간대/경도 해석 (Slice 6)

글로벌 서비스의 최대 정확도 리스크: 해외 출생지의 '그 순간' UTC 오프셋을
역사적 시간대 + 서머타임(DST)까지 정확히 해석하는 것. Python stdlib `zoneinfo`
(IANA tzdb)가 날짜별 역사적 DST를 자동 처리한다.

사용자는 출생 '도시'만 고르면 됨 → (IANA tz, 경도)로 매핑 → 로컬시각을 UTC로.
실서비스에선 지오코딩(도시→위경도) + tz 경계 조회로 임의 도시를 해석하고,
경도는 진태양시에 쓴다(무거운 tz 경계 데이터는 엔진 밖 입력단에서 처리).
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .chart import compute_chart, Chart

# 데모/테스트용 주요 도시 표: name → (IANA tz, 경도 East). 실서비스는 지오코딩으로 대체.
CITIES: dict[str, tuple[str, float]] = {
    "Seoul": ("Asia/Seoul", 126.9780),
    "New York": ("America/New_York", -74.0060),
    "Los Angeles": ("America/Los_Angeles", -118.2437),
    "London": ("Europe/London", -0.1276),
    "Paris": ("Europe/Paris", 2.3522),
    "Tokyo": ("Asia/Tokyo", 139.6917),
    "Sydney": ("Australia/Sydney", 151.2093),
}


def utc_offset_hours(local_dt: datetime, tz_name: str) -> float:
    """해당 로컬시각·시간대의 UTC 오프셋(시). 역사적 DST 자동 반영."""
    aware = local_dt.replace(tzinfo=ZoneInfo(tz_name))
    return aware.utcoffset().total_seconds() / 3600.0


def chart_for_place(local_dt: datetime, tz_name: str, longitude_east: float) -> Chart:
    """출생 로컬시각 + IANA 시간대 + 경도 → 전체 사주 차트 (DST 자동 해석)."""
    return compute_chart(local_dt, utc_offset_hours(local_dt, tz_name), longitude_east)


def chart_for_city(local_dt: datetime, city: str) -> Chart:
    """도시 이름만으로 차트 계산 (CITIES 표 사용)."""
    tz_name, lon = CITIES[city]
    return chart_for_place(local_dt, tz_name, lon)

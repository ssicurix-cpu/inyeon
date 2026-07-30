"""샘플 결과 페이지 생성 — 엔진 전체 파이프라인이 실제로 도는 걸 눈으로 확인."""
import sys
from datetime import datetime

from webapp.reading import build_reading
from webapp.render import render_result

# Emma (뉴욕) × 파트너 Jihoon (서울), 따뜻한 위로형
data = build_reading(
    datetime(1990, 6, 21, 14, 30), "New York", gender="F", persona_key="warm", name="Emma",
    partner={"dt": datetime(1990, 5, 15, 6, 30), "city": "Seoul", "name": "Jihoon"},
)
html = render_result(data)
out = sys.argv[1] if len(sys.argv) > 1 else "result-sample.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", out, "|", len(html), "bytes | eight_char:", data["chart"].eight_char(),
      "| compat:", data["compat"].score, "%")

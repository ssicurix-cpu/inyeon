# 사주 계산 엔진 (Python)

글로벌 K-사주 서비스의 계산 엔진. 정확도가 신뢰의 근간이라, **모든 로직은
독립적으로 검증된 정답지와 단위 테스트로 고정**한다.

## 슬라이스 계획 (한 번에 하나씩)

- [x] **1. 정의 코어** — 천간·지지·오행·음양·지장간·띠 테이블 + 60갑자 유틸
- [x] **2. 일주(日柱)** — 양력일 → 60갑자 (앵커 offset=14, sxtwl 검증)
- [x] **3. 연주(年柱)+띠, 월주(月柱)** — 24절기 경계(입춘 기준, astronomy-engine)
- [x] **4. 시주(時柱)** — 진태양시(경도+균시차) 보정
- [x] **5. 오행 분포·일간·십신·음력 + 전체 차트 조립** — 무료 훅 계산 완성
- [x] **6. 글로벌 시간대·DST 해석** (해외 출생지, IANA tzdb) — 도시만 고르면 계산

**→ 계산 엔진 프로토타입 완성. 외국인(뉴욕/런던) 케이스 검증 완료. 테스트 27개 통과.**

> **미결 결정(Leo 확인):** 자시(子時, 23~24시) 처리 유파차. 기본값은 표준 방식
> (자정 경계·子시 당일 일간). 야자시(晚子時) 옵션은 향후 추가.

## 구조

```
engine/
  saju/core.py          # 정의 코어 + 일주 (Slice 1-2)
  saju/pillars.py       # 연주+띠, 월주 (Slice 3, astronomy-engine)
  saju/hour.py          # 진태양시 + 시주 (Slice 4, 균시차 포함)
  saju/analysis.py      # 오행 분포 + 십신 (Slice 5)
  saju/lunar.py         # 음력 생일 변환 (Slice 5)
  saju/chart.py         # 전체 차트 조립 compute_chart() (Slice 5 capstone)
  saju/place.py         # 도시→시간대/경도, DST 자동 해석 (Slice 6)
  saju/naming/          # 이름 작명: 발음오행 + 이름풀 + 프리미엄작명(A)/Koreanize(E)
  saju/compat.py        # 궁합(간판 훅): 일간 상생상극 + 띠 삼합/육합/충 + 오행보완
  saju/naming/generate.py # + 이름으로 궁합 튜닝(통관 오행 → 상대맞춤 이름, 결제 전환)
  saju/interpret.py     # 경량 해석: "Missing Element" 렌즈 + 3 무당 페르소나(따뜻/직설/신비)
  tests/test_*.py       # 단위 테스트 (정답지 대조, 48개)
  demo.py               # 표준 케이스(서울) 데모 + JSON
  demo_global.py        # 외국인 데모 (뉴욕/런던, 도시만 선택)
  demo_naming.py        # 이름 작명 데모 (외국인 사주 → 한국 이름)
  demo_compat.py        # 궁합 데모 (두 사람 → 궁합 스토리)
  demo_relational.py    # 결제 전환 데모 (궁합 → 이 이름이 조화를 높인다)
  demo_interpret.py     # 해석 샘플 (같은 사실, 3가지 무당 말투)
```

의존성: `astronomy-engine` (순수 파이썬, 외부 데이터파일 없음 → 서버리스 적합).

## 검증 기준 케이스

`1990-05-15 06:30 서울` → 사주 **庚午년 辛巳월 庚辰일 己卯시**, 일간 庚(금),
음력 4월 21일, 말(馬)띠. (lunar_python·sxtwl 두 독립 라이브러리 교차 확인)

## 실행

```bash
cd engine
PYTHONPATH=. python3 -m pytest tests/ -v   # 테스트
PYTHONPATH=. python3 demo.py               # 데모
```

## 정확도 원칙

- 정의 표(천간·지지 순서, 오행 배속, 띠)는 논쟁 여지 없음.
- 계산 로직(일주 앵커 등)은 sxtwl(寿星天文历) 등 독립 라이브러리로 검증한 값만 사용.
- 새 슬라이스마다 알려진 사례로 테스트를 함께 추가한다.

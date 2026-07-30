# Inyeon — 무료 배포 안내 (아침에 따라 하기)

목표: **돈 0원**으로 실제 인터넷 주소에 라이브. 도메인 필요 없음(무료 서브도메인 `...onrender.com`).
소요: 계정 있으면 ~30분, 처음이면 ~1~1.5시간.

준비물(둘 다 무료): **GitHub 계정**, **Render 계정**.

---

## 지금 상태 (Claude가 준비 완료)

- `engine/webapp/app.py` — 하나의 앱이 **랜딩(/) + 입력폼(/start) + 결과(/reading)**를 전부 서빙. 랜딩 버튼은 /start로 연결됨.
- 배포 설정 파일 준비됨: `render.yaml`, `engine/requirements.txt`, `engine/Procfile`, `engine/runtime.txt`.
- 로컬·스모크 테스트 통과(모든 라우트 200). 계정 로그인·배포 실행만 남음(그건 Leo가 클릭).

---

## 1단계 — 코드를 GitHub에 올리기

가장 쉬운 길: **GitHub Desktop**(클릭 방식, 비개발자용).

1. https://desktop.github.com 설치 → GitHub 계정 로그인.
2. `File → Add local repository` → 이 프로젝트 폴더(`E:\빅프로젝트`) 선택.
   - "이 폴더는 저장소가 아니다"라고 하면 `create a repository` 클릭 → 그대로 생성.
3. 왼쪽 아래 요약칸에 아무 메시지(예: "first") 적고 **Commit** → 오른쪽 위 **Publish repository**.
   - **Private로 두는 걸 추천**(코드 비공개). Publish 누르면 GitHub에 올라감.

(git 명령이 익숙하면: `git init && git add . && git commit -m first` 후 GitHub에 새 repo 만들어 push.)

## 2단계 — Render에서 배포

1. https://render.com → **Get Started** → GitHub로 로그인.
2. 대시보드에서 **New +** → **Web Service**.
3. 방금 올린 저장소 선택(**Connect**). 권한 물으면 허용.
4. 설정값 — 대부분 `render.yaml`이 자동으로 채움. 혹시 수동이면:
   - **Root Directory**: `engine`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn webapp.app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type / Plan**: **Free**
5. **Create Web Service** 클릭 → 빌드 로그가 흐름(2~4분). "Live" 뜨면 완료.
6. 상단의 주소 `https://inyeon-xxxx.onrender.com` 가 우리 사이트. 열어서 확인:
   - `/` 랜딩 → "Reveal my chart" 클릭 → `/start` 폼 → 생년월일·도시·무당 입력 → 실제 결과.

## 3단계 — 확인 & 마무리

- `/healthz` 열면 `{"ok": true}` — 정상 신호.
- **무료 플랜 주의:** 15분 정도 방문 없으면 잠들고, 다음 첫 요청이 ~30초 느림(콜드 스타트). 검증 단계엔 문제없음. (나중에 트래픽 생기면 유료/다른 호스트로.)
- 공유 카드의 워터마크 `inyeon.app` 자리는 나중에 실제 주소(또는 확정 도메인)로 바꾸면 됨.

---

## 로컬에서 미리 돌려보기 (선택)

```bash
cd engine
pip install -r requirements.txt
uvicorn webapp.app:app --reload
# 브라우저에서 http://localhost:8000
```

---

## 막히면

각 단계에서 에러 화면/로그를 캡처해서 물어보면 그 자리에서 같이 해결. 빌드 실패는 보통
파이썬 버전(runtime.txt=3.11.9)이나 Root Directory(engine) 설정에서 나옴 — 거기부터 확인.

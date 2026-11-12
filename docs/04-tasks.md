# 04. 작업 목록

MVP 를 3개 Phase 로 진행한다. **Phase 이름과 개수는 아래 3개 그대로 고정한다. 변경 금지.**

| Phase | 이름 | 내용 | 단계 수 |
|---|---|---|---|
| 1 | 설계 | `CLAUDE.md` + `docs/` 6종 작성 | 10 |
| 2 | 백엔드 | `backend/` FastAPI > API 7개 + 받아쓰기 | 10 |
| 3 | 프론트 | `frontend/` HTML + JS + Tailwind > 화면 4종 > API 연결 | 8 |

## 진행 규칙

- **순서대로만** 진행한다. 앞 단계가 끝나기 전에 다음 단계로 넘어가지 않는다
- **병렬 금지.** 두 단계를 동시에 진행하지 않는다
- **단계별 검증 필수.** 「검증 방법」을 실제로 해 보고 통과해야 「완료」를 `[x]` 로 바꾼다
- 「완료」 열은 `[ ]` 로 두고, 진행하면서 `[x]` 로 바꾼다

### 명령어 뜻

| 지시 | 범위 |
|---|---|
| `backend 진행해` | Phase 2 전체 (2.1 ~ 2.10) |
| `frontend 진행해` | Phase 3 전체 (3.1 ~ 3.8) |

## Phase 1 - 설계

`CLAUDE.md` + `docs/` 6종 작성.

| 단계 | 검증 방법 | 완료 |
|---|---|---|
| 1.1 `CLAUDE.md` 작성 - 역할 · 기술 스택 · 작업 시작 전 절차 · 절대 규칙 | 4개 섹션이 있고 투두가드 운영 규칙이 지워지지 않았는지 확인 | [x] |
| 1.2 `docs/` 6종 파일 생성 | `ls docs` 에 6개 이름이 그대로 있고 다른 문서가 없는지 확인 | [x] |
| 1.3 `CLAUDE.md` 의 docs 파일명 · 순서 대조 | `CLAUDE.md` 의 목록과 `docs/` 6개 이름 · 순서가 같은지 비교 | [x] |
| 1.4 `docs/화면구성.pdf` 배치 | 4개 화면 + 요소 이름 표(5쪽)가 있는지 확인 | [x] |
| 1.5 `00-overview.md` 작성 | 매핑표 · 읽는 순서 · 화면 4종 · 디자인 · 관심사 분리가 있는지 확인 | [x] |
| 1.6 `01-product.md` 작성 | 목표 · 페르소나 · MVP 범위 · UI 톤 · 확장 · 범위 외 · 성공 기준이 있는지 확인 | [x] |
| 1.7 `02-specs.md` 작성 | 모델 8필드 · 구분 기준 · API 7개 · 검색 · 검증 · 시각 · 실패 처리 · 화면 명세가 있는지 확인 | [x] |
| 1.8 `03-design.md` 작성 | 기술 결정 표 8행(4열) · 요소 이름 표 · 의존성 정책이 있는지 확인 | [x] |
| 1.9 `04-tasks.md` 작성 | Phase 3개 · 단계 수 10 / 10 / 8 · 열 3개인지 확인 | [x] |
| 1.10 `05-conventions.md` 작성 + 첫 커밋 | `05-conventions.md` 가 채워졌고, 커밋이 GitHub 에 push 되었는지 `git status` 로 확인 | [x] |

## Phase 2 - 백엔드

`backend/` FastAPI > API 7개 + 받아쓰기.

- **서버 포트는 8000 으로 고정한다.** (`uvicorn ... --port 8000`)
- **의존성은 아래 8개로 한정한다. 이 목록 밖은 추가하지 않는다.**
  `fastapi` · `uvicorn` · `sqlalchemy` · `pytest` · `httpx` · `google-genai` · `python-multipart` · `python-dotenv`
- pytest 실행 시 `httpx2` 설치 권고가 떠도 무시한다

| 단계 | 검증 방법 | 완료 |
|---|---|---|
| 2.1 `backend/` 골격 + 의존성 8개 설치 | `requirements.txt` 에 8개만 있고 `pip install` 이 성공하는지 확인 | [x] |
| 2.2 설정 읽기 - `.env` 의 `GEMINI_API_KEY` · `GEMINI_MODEL` | 코드에 키 문자열이 없는지 grep, 설정 로딩 테스트 통과 | [x] |
| 2.3 DB + Meeting 모델 (8필드, `sqlite_autoincrement`) | 생성된 테이블 DDL 에 `AUTOINCREMENT` 가 있는지, 지운 id 가 다시 쓰이지 않는지 pytest | [x] |
| 2.4 요청 스키마(`extra="forbid"`) + 검증 실패 400 예외 핸들러 | 필수 필드 누락 400, 스펙 외 필드 422 pytest | [x] |
| 2.5 회의록 CRUD 5개 - `POST` · `GET` 목록 · `GET` 단건 · `PUT` · `DELETE` `/api/notes` | 201 / 200 / 200 / 200 / 204, 없는 id 404, 목록에 `body` 없음 · 단건에 있음 pytest | [x] |
| 2.6 목록 검색 - `q` · `from` · `to` | 제목 · 참석자 부분 일치, 본문 미검색, 양끝 포함(`to` 23:59:59) pytest | [x] |
| 2.7 세 갈래 구분 - Gemini 호출 (02-specs 기준 프롬프트) | 실제 Gemini 를 불러 pytest(05-conventions): 회의 본문이 세 갈래로 나뉘어 저장, 20자 미만이면 세 칸 빈 값, 회의 내용이 아니면 세 칸 빈 값 | [x] |
| 2.8 `GET /api/todos` | 필드 `what` / `who` / `when` / `note_id` / `note_title`, 회의 날짜 오래된 순 pytest | [x] |
| 2.9 `POST /api/upload` - 받아쓰기 | mp3 · wav 외 415, 25MB 초과 413, 실제 Gemini 로 녹취 파일을 받아써 200 + 본문 pytest | [x] |
| 2.10 포트 8000 실행 + 전체 테스트 | 전체 pytest 통과, `http://localhost:8000/api/notes` 응답 확인 | [x] |

## Phase 3 - 프론트

`frontend/` HTML + JS + Tailwind > 화면 4종 > API 연결.

- 화면 4종은 `02-specs.md` 화면 명세와 `03-design.md` 표대로 만든다
- 파일은 `frontend/index.html` 과 `frontend/app.js` 2개만 둔다
- 프론트는 백엔드가 같은 오리진(포트 8000)에서 제공한다. `file://` 로 직접 열지 않는다

| 단계 | 검증 방법 | 완료 |
|---|---|---|
| 3.1 공통 골격 - 상단 고정 헤더(제목 · 탭 3개 · 테마 버튼), `max-w-6xl` 가운데 정렬, 백엔드에서 제공 | `http://localhost:8000/` 에서 화면이 열리고 탭이 바뀌는지 확인 | [ ] |
| 3.2 테마 토글 - 라이트 / 다크, localStorage, 초기값 시스템 설정 | 토글 후 새로고침해도 유지, 저장값 지우면 시스템 설정을 따르는지 확인 | [ ] |
| 3.3 목록 화면 | `docs/화면구성.pdf` 1쪽과 배치 비교, 카드 2열(360px 1열) 확인 | [ ] |
| 3.4 넣기 화면 | `docs/화면구성.pdf` 2쪽과 배치 비교 | [ ] |
| 3.5 상세 화면 (겹침 창) | `docs/화면구성.pdf` 3쪽과 배치 비교, 바깥 영역 누르면 닫히는지 확인 | [ ] |
| 3.6 할 일 화면 | `docs/화면구성.pdf` 4쪽과 배치 비교, 좁은 화면에서 표만 가로 스크롤 확인 | [ ] |
| 3.7 요소 이름 대조 | `index.html` 의 id 가 `03-design.md` 「화면 요소 이름」 표와 하나도 빠짐없이 같은지 대조 | [ ] |
| 3.8 API 연결 | 01-product 성공 기준 4개를 화면에서 확인 - 녹취 파일 하나가 세 갈래로 저장, 새로고침해도 유지, 360px 에서 안 깨짐, 검색으로 지난 회의를 찾음 | [ ] |

# BID OWL — 새 대화 첫 번째로 읽기
**현재 GitHub: https://github.com/hibi89/Bid_Owl** (구 project08-bid-insight, 동일 저장소).
재개 문구: `[Bid_Owl 깃헙 레포지토리 보고 작업이어가셈]`.

## 즉시 행동
1. GitHub `main`과 `feature/bid-owl-v1-basic-mvp` HEAD 확인.
2. `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, `NEXT_TASK.md`, `REQUIREMENTS.md` 순서로 읽기.
3. 이미 승인된 내용을 다시 묻지 말고 `NEXT_TASK.md`의 **최신 미완료 단계부터** 실제 구현 + 가능한 검증 + 커밋. 2026-10-27 기준 P2-17까지 진행하며 기존 CLI 백업 선행·프로필 변경 거부·지문 저장 호환성까지 보강. 다음은 P2-18의 기존 DB 재생성 경쟁 조건 방지. 실제 CSV 등록은 `START_BID_OWL_IMPORT.cmd` / `backend/import_local.py`, 가상 데모는 `START_BID_OWL_DEMO.cmd`.
4. 코드 변경은 feature 브랜치에서만, main 교육용 데모는 보존. 차단사항은 기록하고 가능한 작업 진행.
5. 작업 후 STATUS/HANDOFF 갱신과 정확한 최신 SHA 보고.

## 확정 V1.0
- 브랜드 BID OWL(비드아울), '올빼미의 관찰하는 눈' — 국내 상표권 사용 가능성은 확인 필요.
- Windows 로컬 설치형, Python+SQLite 신규 엔진+기존 HTML/JS/CSS 일부 재사용.
- BASIC 59,000원 CSV+자격 3상태+근거+Excel/PDF.
- PRO 149,000원 공식 나라장터 API 증분 수집+PC 실행 중 갱신/로컬 알림.
- PREMIUM 299,000원 선택형 고객키 문서 AI+수익 시뮬레이션.
- 1회 구매 / 고객 월 필수 사용료 0원 목표, 외부 AI는 고객 과금.
- 디자인: Stotles/GovDash식 검색·테이블 중심 B2B, 7종 테마(cloud, obsidian, midnight, graphite, emerald, sand, iris).
- 일정: 3일 첫 BASIC MVP, 전체 17~18 작업일(65~100시간 추정). 채팅 밖에서 자동 작업이 진행되지는 않음.
- 판매: 크몽 → 네이버/무료 데모 → 숨고, 브랜드 법적 확인 전 공개 판매 보류.

## 레거시 주의
- `README.md`는 기존 학원 정적 데모용 설명.
- `app.js`의 정적 340/340 PASS와 `data.js`의 2025년 고정 D-Day는 상용판 검증 근거 아님.
- Vercel git 연결은 rename 후 미검증. public 배포/운영 설정 변경 금지.


## P2-13 로컬 체험 진입점
- GitHub 개발 브랜치 최상위 `START_BID_OWL_DEMO.cmd`: 합성 공고 2건 전용 Python 로컬 브라우저 체험. 배포/실사용 완제품 아님.
- `backend/DEMO.md`: 데이터 격리와 실행·정리·미검증 상태 설명.
- 사용자는 반복적인 수동 Windows QA·ZIP 다운로드 요청을 원하지 않음. 일상 ㄱ 진행은 AI가 GitHub 개발·검수·문서 작업으로 처리하고 실제 Windows 검증은 출시 게이트로 명시.

## P2-14 로컬 회사·CSV 온보딩
- 개발 브랜치 최상위 `START_BID_OWL_IMPORT.cmd`: Tkinter 파일 선택, 회사 프로필 입력, 사전 검증·확인 후 기존 DB 백업과 명시적 저장.
- 백엔드 `backend/import_local.py` CLI 기본 동작은 PREVIEW_NO_WRITE; 실제 저장은 `--apply`. `backend/IMPORT.md` 참고.
- 사용자에게 반복적인 ZIP/PowerShell QA를 시키지 말고 AI가 가능한 개발·정적 검증을 수행한다. 진짜 Windows 런타임 검증은 나중 출시 관문으로 표기.

## P2-15 재등록 평가 및 다음 P2-16
- `backend/import_local.py` 동일 공고와 동일 회사 버전·마감 상태이면 과거 판정 재사용, 변경 시 새 스냅샷 추가. GUI 전체 재평가 체크 및 CLI `--force-reassess`.
- 평가 엔진 코드 버전 변화는 아직 자동 비교하지 못하므로 코드 업데이트 후 강제 재평가가 필요. P2-16 우선순위는 **평가 엔진 변경 시 캐시 자동 무효화**, 구버전 스냅샷은 과거 근거로만 보관.
- GitHub 테스트 선언 178개, 실 Python 전체 PASS 아님. 형에게 반복 다운로드나 Windows QA 요청하지 않기.

## P2-16 규칙 엔진 판정 현재성
- 저장된 공고 버전/회사 프로필 버전/판정 엔진 SHA-256이 모두 일치해야 현재 PASS로 표시. 구형 DB나 누락된 지문은 UNKNOWN.
- 구형 DB는 정상 백업을 먼저 만든 뒤 추가 메타데이터 테이블 생성. 판정 이력 보존.
- 근거·제한 문서: `backend/ENGINE_POLICY.md`; 최신 개발은 P2-17부터. 완료 코드와 실행된 전체 테스트를 혼동하지 말 것.

## P2-17 구형 CLI 호환성 개선
- 구형 `backend/cli.py` CSV/PDF/XLSX 경로가 기존 SQLite를 수정하기 전에 읽기 전용 검사와 비덮어쓰기 백업을 수행하도록 보강. 규칙 엔진 지문 테이블은 백업 이후에만 보강.
- 소스 검토와 9개 신규 테스트 정의 반영. 전체 Python **199개 정의 테스트는 실제 실행 검증되지 않음**. 사용자에게 반복적인 ZIP/PowerShell 테스트 요청 금지.

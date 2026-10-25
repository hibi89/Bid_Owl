# NEXT_TASK — 첫 번째 BID OWL BASIC MVP 코드 구현
기준: 2026-10-26 / 상태: 신규 기능 미착수
저장소: `hibi89/Bid_Owl`, 작업 브랜치: `feature/bid-owl-v1-basic-mvp`.

## P1-00 착수
- 브랜치 main/feature HEAD 조회, 레거시 `app.js`/`data.js` 구조 파악, 백업 가능한 commit 기준 확인.
- feature 브랜치만 편집. Vercel 설정, main HTML/JS/CSS/고정 데이터는 아직 수정 금지.
- Python 3 표준 라이브러리 중심으로 단위테스트 가능한 신규 모듈부터 시작. 비용 드는 외부 API가 없어도 진행.

## P1-01 CSV import + 스키마 + 테스트
- 제안 파일: `backend/bidowl/__init__.py`, `backend/bidowl/schema.py`, `backend/bidowl/importer.py`, `backend/tests/test_importer.py`, `backend/fixtures/sample_bids.csv`.
- 최소 CSV 컬럼: `bid_no,title,agency,category,bid_deadline,budget,requirements` (요건은 정의된 JSON 형식 등으로 명세).
- 빈 필드, 중복 공고번호, 비정상 날짜, 숫자, UTF-8-SIG 처리. 임의 보정 금지, 구조적 오류 보고.
- 테스트: 정상, 누락, 중복, 기간 만료, 잘못된 금액, 인코딩. 샘플과 실제 데이터 반드시 구분.

## P1-02 회사 프로필·자격 판정
- 제안 파일: `backend/bidowl/profile.py`, `backend/bidowl/eligibility.py`, `backend/tests/test_eligibility.py`.
- 입력: 회사 지역/분류/면허/실적/인원 등, 공고 조건과 원문 위치/출처.
- 각 요건은 `PASS`, `FAIL`, `UNKNOWN` 하나만. 증빙 없음/알 수 없는 법규는 UNKNOWN, 임의 낙찰률 생성 금지.
- 테스트: 충족, 불충족, 정보 부족, 여러 요건, 프로필 변경, 출처 추적.

## P1-03 SQLite 영속 저장
- 제안 파일: `backend/bidowl/store.py`, `backend/tests/test_store.py`.
- 공고 원본/변경 이력, 회사 프로필, 판정 및 근거, import 실행 감사 기록.
- 파라미터 SQL, 트랜잭션, 동일 파일 재입력 중복 방지, 중단/재실행과 reopen 저장 확인.
- 테스트: 중복/업데이트/rollback/다중 프로필 결과 구분.

## P1-04 최소 보고서·동작 확인
- 제안 파일: `backend/bidowl/report.py`, `backend/cli.py`, `backend/tests/test_report.py`.
- CSV + 프로필 → SQLite → 3상태 판정 → 실제 근거 확인 → Excel/PDF.
- 한국어 보고서와 날짜/출처/판정 근거, '자동 판단 참고용' 고지.
- 라이브러리·폰트 라이선스 확인. 실제 PDF 한국어 렌더/엑셀 파일 검증 후만 PASS. 불가 시 미검증으로 기록.
- 간단한 로컬 실행법과 샘플 fixture 사용법을 문서로 제공.

## 이후
- UI 교체/7테마, BASIC 완료 → PRO API→ PREMIUM AI → Windows 설치·보안→ 크몽 체험판/판매.
- 끝내기 전 STATUS.md·HANDOFF.md 커밋에 테스트 명령, 성공/실패/미실시 수, SHA, 다음 TODO 기록.
- 상품 설계는 REQUIREMENTS.md, ROADMAP.md가 기준.

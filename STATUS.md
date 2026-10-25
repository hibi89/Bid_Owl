# BID OWL — STATUS (2026-10-26 KST)

## 정확한 저장소와 상태
- 현재 Repo: **hibi89/Bid_Owl** (private, 기본 `main`), repo ID `1399359397`.
- 구 이름: `hibi89/project08-bid-insight` (동일 저장소). 2026-10-26 사용자 직접 rename 확인.
- 사용자 선택 상용 제품명: BID OWL/비드아울. 기존 BID INSIGHT 정적 학원 데모 UI는 남아 있음.
- 현재 수준: **제품 설계 확정 / 새 분석·설치 제품 코드 미구현 / GitHub 문서 인수인계 준비 완료**.
- 원본 레거시 SHA `2807a93a3e0deba98840712401fdd6025e6f5610`, rename 인수인계 전 SHA `4c2f26f36abe35c4fd0ac8ce1bc633566c96f24c`.
- 개발 전용 브랜치: `feature/bid-owl-v1-basic-mvp` (다음 턴에서 실제 최신 HEAD 확인).

## 완료된 것(확인 사실)
- 기존 데모 구조 확인: 2025-08-10 샘플 20건, JavaScript 렌더, 로컬스토리지 즐겨찾기, 정적 PASS/Judge. 신규 엔진 없음.
- 7테마 B2B UI 디자인 방향 및 3티어 기능 범위 확정.
- BASIC 59,000 / PRO 149,000 / PREMIUM 299,000원 (1회 구매), 고객 필수 월 사용료 0원 목표.
- 추가 현금 예산 0~50,000원 목표(개발 인건비·서명 등 미포함).
- 개발 17~18작업일, 첫 3일 MVP 계획 수립 (실제 착수/완료 기록 아님).
- 브랜드 BID OWL 명칭 선정, 국내 상표 법적 적합성 미검증.
- README는 학원 데모 설명; START_HERE/AGENTS/HANDOFF/NEXT_TASK가 상용 작업기준.

## 다음 단계
- NEXT_TASK.md P1-01 ~ 04: Python CSV/프로필/자격 판정/SQLite/PDF·Excel 실제 구현 및 가능한 테스트.
- 신규 feature 브랜치만 변경, 기존 main 웹코드와 운영 배포는 유지.

## 미검증/차단
- 새 분석 코드·7테마·API 연동·Windows 실기기 테스트·크몽 판매: **미구현/미실시**.
- KIPRIS·도메인/유사 브랜드: **사용 권리 미확정**, 공개 출시 보류.
- Vercel 구 프로젝트는 조회 가능, 최신 READY 상태 표시. 새 GitHub `repo=hibi89/Bid_Owl` 목록 필터 결과 0건. Git 연결/Production SHA/웹 접속은 **미검증**. 사전 승인 없이 설정 바꾸지 말 것.
- 교육용 `340/340 PASS`는 새 테스트 실행 결과가 아님. 현재 테스트 수 **0건 실행**.
- 고객 PC가 실행 중일 때만 PRO 갱신/알림. 항상 켜진 서버 서비스 아님.

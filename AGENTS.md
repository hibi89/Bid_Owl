> **[KMONG_WORK_TARGET_GATE_20261112 | 사용자 최신 확정 | 필수 작업 규칙]** 이 저장소에서 크몽 상품·육성 후보를 작업하는 모든 AI 담당자는 새 채팅·`ㄱ` 시작 시 이 문구를 읽고 적용한다.
> - 실제 개발/수정/테스트 착수 즉시 [해총 크몽 최종완성률·후보 상태표](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/audits/KMONG_16_CURRENT_20261111.md)의 **해당 상품명 옆에 `**[작업중]**`을 표시하고 GitHub 커밋**한다. 확정 단계 목표(예: 95%)와 검증 기준을 제품 STATUS/HANDOFF에 남긴다.
> - **목표 완성률 달성 전에는 [작업중]을 삭제하지 않는다.** 일시중단·종료·보류·다른 제품 전환·담당 채팅 변경도 삭제 사유가 아니다. 예전 '전환·중단 시 삭제' 지시는 폐기한다.
> - **검증된 목표치에 도달한 뒤에만** 기능 SHA·PASS/FAIL/SKIP·미검증을 기록하고 자기 표시를 제거·커밋한다. 목표 하향/변경으로 표식 제거 시 사용자 명시 승인 필요. 다른 담당자 표시·기존 수치·RELEASE HOLD 보존.
> - 표식은 목표 미달 상태를 의미하며 **실시간 실행 증명은 아니다**. 허브 최신 HEAD 확인 후 안전하게 반영, 실패 시 `KMONG_HUB_SYNC_PENDING` 기록. 자동 동기화 없음. 크몽 외 작업에는 표시 불필요.

> **2026-10-28 해총 전 저장소 최상위 공통 운영 공지 (소유자 승인):** [개발 가속·로컬검증·병목제거 통합 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/main/docs/DEV_ACCELERATION_AND_VERIFICATION_20261028.md)을 새 채팅에서 먼저 확인한다. 현재 활성 개발 4개 슬롯은 **KIC(+DL)·PayPal·UGREEN·LA**만이다. 본 프로젝트는 **임시 개발 대기(폐기·브랜치 삭제 아님)**: 소유자 재개 지시 전 `ㄱ`으로 임의 기능 구현·CI·배포하지 않는다. 활성 총괄의 일반 구현·검증은 **GPT-6 Instant**, 최초 설계·고위험 문제·해총 감독은 높은 추론. 파일 단위 GitHub 왕복·다중 상태 문서 갱신·중복 CI를 축소하며 검증된 기능과 정확한 Git SHA/PASS·FAIL·SKIP만 보고한다. 기존 설계 동결·보안·고객 데이터·외부 서비스·금전/제출 승인 규칙은 유지한다. 본 공지는 제품 기능 변경이나 검증 완료가 아니다.

# BID OWL — GitHub 개발 운영 규칙
갱신: 2026-10-26 KST
실제 저장소: **hibi89/Bid_Owl** (private, GitHub repository ID 1399359397)
이전 저장소 이름: hibi89/project08-bid-insight (동일 repository의 옛 주소).
제품명: **BID OWL / 비드아울**. 옛 BID INSIGHT는 교육용 데모 코드/데이터의 과거 표기.

## 새 채팅 자동 작업 재개
사용자가 `[Bid_Owl 깃헙 레포지토리 보고 작업이어가셈]`라고 보내면:
1. **실제** GitHub 저장소 hibi89/Bid_Owl의 main/개발 브랜치 최신 HEAD를 조회한다.
2. `START_HERE.md`, `STATUS.md`, `HANDOFF.md`, `NEXT_TASK.md`, `REQUIREMENTS.md`를 읽는다.
3. 묻지 않고 `feature/bid-owl-v1-basic-mvp`에서 가장 먼저 미완료된 BASIC MVP 작업을 **실제 코드 구현 + 가능한 테스트 + 커밋**으로 진행한다. 브랜치가 없으면 main에서 분기한다.
4. 사용자에게 이미 결정된 이름/디자인/상품가/아키텍처를 다시 질문하지 않는다. 외부 서비스 승인·결제·실사용 키처럼 사용자 작업이 필요한 항목은 차단으로 적고 다른 작업을 이어간다.
5. 마무리 때 `STATUS.md`, `HANDOFF.md`에 현재 SHA·변경 파일·검증/미검증·다음 작업을 기록한다. `ㄱ`은 다음 작업 진행 신호.

## 변경 규칙
- `main`의 기존 2025년 학원 정적 데모(index.html, app.js, data.js, CSS, assets)를 보호. 신규 기능은 feature 브랜치. 강제 push, 데이터 삭제, 운영 배포/환경 설정 변경은 승인 없이는 금지.
- 데모 고정 데이터 20건, QA 숫자 340/340, 2025-08-10 기준 days_left는 **실제 현재 판정 결과가 아님**. 새 도구의 검증 수치로 인용하지 말 것.
- Python+SQLite 로컬 신규 분석 엔진, UI 자산 일부 재사용, 7종 테마. BASIC → PRO → PREMIUM → Windows 설치·통합 검증. P1 상세는 NEXT_TASK.md.
- PASS/FAIL/UNKNOWN·근거·사용자 확인으로 안전하게 판정. 알 수 없는 자격은 UNKNOWN. 실시간 마감일 재계산, 원본 기준일 표시.
- API 키/고객 문서/개인정보/SQLite 데이터 GitHub 커밋 금지. Python localhost 바인딩, 파라미터 SQL, 파일 검증, 토큰 마스킹 등 초기 보안 필수.
- 유료 도구·외부 데이터 전송·대외 판매·Vercel 설정·기존 main 코드 변경은 사전 사용자 승인.
- 상표 BID OWL은 사용자 선택됐으나 KIPRIS 법적 사용 가능성 미검증(기존 BiddingOwl 연관). 공개 판매는 검증 후.
- 사용자 PC가 켜진 상태에서만 공고 자동 갱신/알림. 24시간 클라우드 감시로 홍보 금지.
- 문서 설계/테스트/배포/실사용 사실을 구분. 실제 실행 증거 없는 완료 주장 금지.
- 레거시 원본 복구 SHA: `2807a93a3e0deba98840712401fdd6025e6f5610`. Rename 전후 기존 repo ID 동일.

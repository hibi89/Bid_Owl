# BID OWL — 새 채팅 인수인계 (최신 단일 기준)
갱신: 2026-10-26 KST

## 0. 즉시 재개 지시
프롬프트: `[Bid_Owl 깃헙 레포지토리 보고 작업이어가셈]`
해당 메시지에서 **추가 설명을 요구하지 말고**, 이 파일과 START_HERE, NEXT_TASK 및 코드 구조 확인 후 첫 미완료 작업부터 착수한다.

## 1. 저장소/브랜치/인증/원본
- 실제 GitHub **https://github.com/hibi89/Bid_Owl** (비공개), 기본 브랜치 `main`.
- 사용자가 기존 `hibi89/project08-bid-insight`를 `Bid_Owl`로 직접 rename. repo ID 전후 모두 `1399359397`. 대소문자는 GitHub 표시값인 `Bid_Owl`.
- 연결 GitHub 주체 `hibi89`에게 push 권한 있음을 이관 당시 확인. 다음 턴 다시 확인.
- Rename 인수인계 이전 main SHA `4c2f26f36abe35c4fd0ac8ce1bc633566c96f24c`; 최신 HEAD는 새로 조회해야 함. 교육용 데모를 되돌릴 수 있는 SHA `2807a93a3e0deba98840712401fdd6025e6f5610`.
- BASIC 신규 코드 브랜치: **`feature/bid-owl-v1-basic-mvp`**. 없으면 생성, `main` 기존 웹앱 코드 수정/병합 금지.

## 2. 브랜드/제품 방향(확정)
- **BID OWL / 비드아울**: 올빼미 눈처럼 공고를 지켜보며 자격요건/위험/근거를 확인. 이전 비드인사이트 및 비드아카이브는 폐기된 브랜드 후보.
- 중소기업용 Windows 11 **로컬 설치형** 조달/공공입찰 검토 소프트웨어. 자체 클라우드 서버 필수 없음.
- 디자인: Stotles/GovDash 계열 B2B 정보 중심, 검색·필터·테이블+근거 패널, 과도한 KPI/장식 금지.
- CSS 디자인 토큰 7종: cloud, obsidian, midnight, graphite, emerald, sand, iris (라이트 4/다크 3).
- 기본 기술: 기존 HTML/JS/CSS UI 일부 재사용, **Python 신규 로컬 분석 엔진 + SQLite**, 공식 조달청 입찰공고 API(사용자 키), 선택형 문서 AI(고객 키).
- BASIC 59,000원: CSV/회사 프로필/근거 포함 PASS·FAIL·UNKNOWN/리스크/검색/PDF·Excel.
- PRO 149,000원: 공식 나라장터 데이터 수집·정정/증분·중복방지·PC 실행 중 로컬 알림.
- PREMIUM 299,000원: 고객 선택 AI PDF/DOCX 텍스트 분석·근거·원가 시뮬레이션/예산 통제.
- 1회 구매, 고객 월 필수 이용료 0원 목표. 고객 AI 호출료는 고객 부담. 추가 개발자 현금비 목표 0~50,000원(인건비/코드 서명/판매 비용 제외).
- 크몽 우선 → 네이버 블로그/무료 데모 → 숨고 맞춤 설치. 상표·브랜드 권리 확인 전 공개 판매 보류.
- 예상 17~18 작업일(빠르면 14일) / 65~100시간, 3일 BASIC 핵심 MVP 목표. **실제 백그라운드 자동 작업/완성 납기 약속 아님.**

## 3. 저장된 레거시 코드 및 위험
- 이전 앱은 2025-08-10 학원 샘플 20건 기반 정적 PWA; README, index.html, redesign.html, app.js(~36KB), data.js(~105KB), styles.css(~93KB), editorial.css, vercel.json 등.
- 현행 app.js `window.PROJECT08_DATA`의 사전 점수·시뮬레이션·QA 숫자를 표시. Python 원본/실제 수집 파이프라인/원본 공고 PDF는 repo에 없음.
- 화면의 `340/340 PASS`는 20건 x 17 체크목록의 **표시용 계산**이지 새 코드의 테스트 실행 결과가 아니다.
- `days_left`는 2025-08-10 기준 고정 수치; 실제 공고에서는 마감일+현지시각으로 재계산.
- `README.md`의 `python -m http.server 8000`은 **기존 정적 웹앱 사용법**이지 신규 앱 실행 명령 아님.

## 4. 실작업 현황·검증 결과
- 지금까지 완료: 저장소 분석, 상용 V1.0 설계, 브랜드명 결정, 상품/디자인/비용/일정 문서화, GitHub rename 확인, 다음 작업 계획/브랜치 준비.
- **미구현:** 신규 CSV 파서/자격 엔진/SQLite/Excel PDF/7테마/PRO API/PREMIUM AI/Windows 설치/상용 QA.
- 이번 이관 작업: 문서/개발 브랜치 설정만. 신규 Python 테스트 실행 **미실시**(통과 0/실패 0), 실제 앱 동작 미검증.
- Vercel 프로젝트 `project08-bid-insight` ID `prj_YcrN7OdOjKl6M457HelGIItLeeXZ` 확인. 최신 deployment 상태 READY 메타데이터 관측.
- **주의:** Vercel `list_projects(repo=hibi89/Bid_Owl)` 응답은 0건; rename 후 Git 자동연결/Production SHA/익명 접속/브라우저 동작은 미검증. docs 커밋을 실제 배포 성공으로 주장하지 말 것.

## 5. 최초 실행 작업/인수인계
1. 현재 GitHub HEAD/feature 브랜치 최신값 확인. START_HERE.md, NEXT_TASK.md, REQUIREMENTS.md 및 레거시 코드 재확인.
2. `feature/bid-owl-v1-basic-mvp`에서 P1-01 CSV/schema/fixture/테스트 → P1-02 규칙 3상태 판정 → P1-03 SQLite 및 중복/이력 → P1-04 최소 PDF/Excel로 단계적 구현.
3. 실제 테스트 가능한 범위에서 테스트 실행, 수치·예외 보고, GitHub에 commit. local Python 실행이 필요한 경우 가능한 도구를 활용하되 테스트가 불가능하면 그대로 미검증 표시.
4. 동일 질문 반복 금지. 사용자는 `ㄱ`을 다음 단계 진행 신호로 사용함.
5. 종료 전 STATUS.md/HANDOFF.md 최신화, 다음 미완료 작업 명시.

## 6. 공개 전 해결해야 할 일
- KIPRIS BID OWL/BIDOWL/비드아울, 유사 BiddingOwl 상표 및 도메인/로고. 법적 권리 미검증.
- 조달청 API 실 키/호출 제한/상용 이용 정책, 스캔 PDF 제외 조건, 고객 AI 외부 전송 사전 동의.
- Windows 실기기 설치/데이터 복구/유료 모델 비용/보안/라이선스/고객 계약/크몽 등록 검증.
- 고객 PC 종료 후에는 감시하지 않음. 자동 투찰·법적 자격 보증·낙찰 확률 보장 기능 없음.

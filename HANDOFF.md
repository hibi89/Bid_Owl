# 다음 채팅 인수인계 — 2026-10-26 01:29 KST

## ① 목표·확정 요구·기술
- hibi89/project08-bid-insight 정적 교육용 UI를 재사용하여 Windows 로컬형 중소기업 공공입찰 검토 솔루션 V1.0 개발.
- BASIC 59,000 / PRO 149,000 / PREMIUM 299,000원 1회 구매, 필수 월 이용료 0원 목표, Python+SQLite+HTML/JS, 공식 조달 API, 선택형 AI.
- 7개 전체 테마(클라우드·옵시디언·미드나잇·그래파이트·에메랄드·샌드·아이리스). 자세한 명세 REQUIREMENTS.md/DESIGN_SYSTEM.md.

## ② 완료 기능·변경·결정 근거
- 기존 app.js/index.html/data.js 기반 2025년 고정 20개 공고를 보여주는 UI/디자인이 있음. 신규 실제 수집/분석 기능을 구축한 것은 아님.
- 설계 비교: 정적 JS 확대는 데이터·상태 관리 한계, 전체 신규는 UI 자산 낭비. **UI 재사용+Python 판정 엔진 새로 구현** 채택.
- 이번 작업은 요구/브랜드/비용/디자인 문서 추가만. 런타임 코드는 변경하지 않는다.
- 국내 동명 BID INSIGHT 서비스 존재: https://bidinsight.co.kr/. 사용자가 신규 작업명 **비드아카이브(BID ARCHIVE)** 채택. bidarchive.io 영문 동명 경매 사이트 사용 확인; KIPRIS 9/35/42류 등 미확인으로 공개 출시는 보류.

## ③ 테스트 명령·결과·검증/미검증
- 이번 작업은 정적 문서 추가. Python, node, UI 기능 테스트 실시하지 않음(성공 0/실패 0/미실시).
- 확인된 기존 데모의 실행 안내는 README.md의 'python -m http.server 8000' (이번에 실행한 결과 아님).
- 340/340 PASS는 UI 코드가 고정 산식으로 표시하는 값이며 신규 테스트의 합격 근거로 사용 불가.
- 신규 기준 문서 7개를 GitHub main에 반영한 설계 기준 커밋은 6ae5ad8d6536533d308bbd0769542776ca32a830. HEAD/문서 7개/수정 파일 목록 확인. 기존 실행코드 수정 0개.

## ④ 현재 단계·중단 지점
- 설계 확정, 코드 개발 대기. 설계 문서 외 구현 미착수.
- 최신 제품명은 **BID OWL(비드아울)** 사용자 선택. KIPRIS·유사 BiddingOwl/BidOwl.com 사용 검토 미완료: **공개 판매/로고 확정/상표 등록 보류**.

## ⑤ 오류·근거·시도·재시도 금지·대안
- 기존 정적 데이터는 2025-08-10 기준, D-Day 고정, 검증 성공 340/340을 화면에서 자체 테스트 없이 표시.
- KIPRIS 개별 상표 등록 여부는 조회되지 않았으므로 상표 가능/불가를 확정하지 말 것.
- 같은 이름으로 크몽 신규 등록하거나 기존 상표를 모방하지 말 것. 별도 후보명 검증을 우선.

## ⑥ 저장소·브랜치·SHA·주요 경로
- Repo: hibi89/project08-bid-insight (private). 기준 브랜치: main.
- 문서 추가 전 HEAD: 2807a93a3e0deba98840712401fdd6025e6f5610; 최신 HEAD는 저장소에서 다시 확인.
- 주요 데모 파일: README.md, index.html, redesign.html, app.js, data.js, styles.css, editorial.css.
- 새 기준 문서: AGENTS.md, REQUIREMENTS.md, DESIGN_SYSTEM.md, PRODUCT_AND_COST.md, BRAND_RESEARCH.md, STATUS.md, HANDOFF.md.

## ⑦ 배포·프로젝트·실행·환경
- Vercel 구성: vercel.json 존재; 공식 URL, 프로젝트명, Production SHA는 이 작업에서 확인하지 않음.
- 데모 실행 안내: python -m http.server 8000; Windows 11 상용판은 미개발.
- Vercel 프로젝트 조회: project08-bid-insight, latestDeployment READY(상태 메타데이터만). 상세 조회 404/배포 목록 403으로 GitHub↔Production SHA 및 실서비스 기능 **미검증**. 문서 추가만으로 서비스 정상이라고 보고하지 말 것.

## ⑧ 원본·백업·인증·수정 금지
- 원본 기준 Git commit SHA 위 기재. 복구는 원본 commit 체크아웃/브랜치 비교 (강제 push/이력 삭제 금지).
- demo assets 및 data.js를 그대로 보존. 고객 파일/실사용 API key/.env/토큰을 GitHub에 올리지 않음.
- 원본 PDF/Python 분석 코드가 이 repo에 없으므로 외부 원본을 임의 추정 금지.

## ⑨ 다음 작업·승인사항·완료기준
- P0 BID OWL(비드아울) 사용 가능성 KIPRIS/선사용 조사(명칭 선택은 승인됨); 기존 repo 이름은 유지.
- P1 개발 브랜치 생성 및 BASIC 수직 슬라이스: CSV→프로필→PASS/FAIL/UNKNOWN→실제 테스트 결과→Excel/PDF.
- P2 공식 API PRO, P3 선택형 AI PREMIUM, P4 Windows 설치·보안·실사용 검증.
- 유료 결제, 새 서비스 연동, 권한/보안/원본 대규모 변경은 사전 승인.

## ⑩ 작성 일시·검증 범위·문서 기준
- 작성: 2026-10-26 01:29 KST.
- GitHub 읽기 확인: 2026-10-26 01:29 KST, main 원본 2807a93a3e0deba98840712401fdd6025e6f5610.
- 설계 문서 기준 커밋: 6ae5ad8d6536533d308bbd0769542776ca32a830 (GitHub에서 SHA·작성자·변경 파일 7개 확인). HANDOFF/STATUS 검증 결과 후속 갱신 커밋은 최신 main HEAD를 조회할 것.

## 2026-10-26 일정·제품명 인수인계 추가
- 추가 기준 문서 ROADMAP.md: 추정 14~18 작업일 / 65~100 인시, 3일 MVP → BASIC 기능 마감 → PRO 공식 API → PREMIUM AI → 설치·보안·판매자료. 연속 진행 가정, 달력 확정 납기 아님.
- 사용자 선택 이름은 비드아카이브(BID ARCHIVE); 영문 동명 https://bidarchive.io/ 확인, 법적 사용 가능성 미검증. 제품·기능 설계 및 가격은 유지.
- 이번 작업은 이름·일정 문서만 수정, 데모/배포 코드 변경 없음. 실제 테스트 명령 실행 성공 0 / 실패 0 / 미실시. 원본 복구 기준 SHA 4b82f38669d579df17437df8820e23bb39c637c3.
- GitHub 최신 SHA는 새 문서 커밋 후 HEAD를 다시 조회할 것. Vercel Production은 이 문서 변경에서 검증 비대상(기존 상세 조회 404·목록 403).

## 2026-10-26 최신 사용자 브랜드 변경 (이 단락이 이전 브랜드 기록보다 우선)
- 기존 BID ARCHIVE(비드아카이브)에서 **BID OWL(비드아울)**로 사용자 지시로 변경. 의미는 '올빼미의 눈처럼 공고를 지켜보고 자격·위험 근거를 탐색하는 제품'.
- 검색에서 해외 BiddingOwl.com 실제 경매 SW 운영, 과거 BidOwl.com 명칭 사용 확인. KIPRIS 국내 상표 결과 미확인, 공개 판매 전 검토 필요 (BRAND_RESEARCH.md).
- BID OWL 브랜딩은 디자인 토큰 7종·가격 3종·예상 14~18 작업일·Windows 로컬 아키텍처에 영향을 주지 않음.
- 로컬 앱이 꺼진 뒤에도 24시간 감시하는 서비스가 아님. 마케팅에서 '상시 24시간' 표현 금지.
- 이번 턴: **문서만 최신화**, 기존 앱·DB·Vercel 코드 수정하지 않음. 실제 신규 기능 테스트 미실시. 다음 턴에서는 GitHub 최신 SHA/STATUS/ROADMAP을 반드시 읽고 개발 재개.

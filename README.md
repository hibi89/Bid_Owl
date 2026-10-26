## BASIC MVP 우선 복귀 — P2-25

현재 개발의 최우선 목표는 CSV·회사 정보 입력 → 입찰 자격 참고 판정 → 로컬 SQLite 증거 저장 → 공고 조회 → Excel/PDF 보고서를 **실제로 끝까지 실행·검증하는 것**이다. 기존 시각 디자인은 보류하고 PRO/PREMIUM도 MVP 통과 이후에 진행한다. 실제 고객 등록기 경로의 자동 수용 검사 소스 `backend/mvp_smoke.py` 및 기준 `backend/MVP_ACCEPTANCE.md`를 추가했다. 현재 GitHub에는 Python 테스트 **256개가 정의**되어 있으나 전체 실행·Windows 출시 검증은 아직 완료되지 않았다.

---

> **P2-14 개발 브랜치 안내:** 실사용 CSV·회사 프로필을 PC에 등록하는 새로운 오프라인 진입점은 `START_BID_OWL_IMPORT.cmd`이며 [backend/IMPORT.md](backend/IMPORT.md)에 설명했습니다. 가상 데이터 전용 `START_BID_OWL_DEMO.cmd`와 별개입니다. 실제 Windows 실행·상용 인증은 미검증 상태입니다.

> **BID OWL 신규 Python 로컬 제품 개발 브랜치 안내 (P2-13)**  
> Windows에서 가상 공고 전용 로컬 데모를 실행하려면 `START_BID_OWL_DEMO.cmd`를 사용합니다. 실제 공고·고객 DB를 사용하지 않으며 실행 중 임시 SQLite를 사용합니다. 상세 설명은 [backend/DEMO.md](backend/DEMO.md), 개발 상황은 [STATUS.md](STATUS.md) 참조. 이 아래의 BID INSIGHT 설명과 340/340 수치는 과거 정적 학원 데모 전용이며 신규 제품 검증 결과가 아닙니다.

# BID INSIGHT — Executive Web / Mobile

경영진(부장·임원급)이 공공·입찰 공고를 빠르게 판단할 수 있도록 구성한 **반응형 웹 + PWA** 버전입니다.

## 핵심 원칙
- **동일 URL**: PC에서는 경영진 대시보드, 모바일에서는 앱형 카드 UI로 자동 전환됩니다.
- **현재 PROJECT 08 데이터 재사용**: 공고 20건, 자격 판정, 점수, 시뮬레이션, Judge 결과를 그대로 사용합니다.
- **사람이 최종 판단**: FAIL/UNKNOWN/Hard blocker 및 QA 근거를 숨기지 않습니다.
- **공개 배포 안전성**: 이 폴더에는 `.env`, API key, 원본 PDF, Python 소스가 없습니다.

## 구현 화면
1. 경영진 대시보드
2. 추천 공고
3. 전체 공고 탐색/필터
4. 리스크 관제
5. 수익성 분석
6. 품질 검증(QA/Judge + Deterministic 340/340)
7. 공고 상세 Drawer
8. 경영진 브리핑 Modal
9. 추가 데이터 연동 로드맵

## 현재 데이터 기준
- 분석 기준일: **2025-08-10 (교육용 데이터)**
- 적극추천 2 / 검토 10 / 패스 8
- Hard blocker 4건
- 평균 예상 마진 12.26%
- Judge 평균 97.8/100
- Deterministic 340/340 PASS

## 향후 추가 데이터만 연결하면 확장 가능한 기능
- 나라장터/지자체 실시간 수집
- 경쟁사·낙찰 이력 분석
- 실제 원가·가용인력 기반 정밀 시뮬레이션
- 사내 승인/CRM 연동

## 로컬 실행
```powershell
python -m http.server 8000
```
브라우저에서 `http://localhost:8000` 접속.

## Vercel 배포
이 폴더에서:
```powershell
npx vercel --prod
```
정적 사이트이므로 별도 Build Command나 환경변수는 필요 없습니다.

## PWA
지원 브라우저에서 설치 이벤트가 제공되면 상단 `+` 버튼으로 홈 화면/앱 형태로 설치할 수 있습니다.

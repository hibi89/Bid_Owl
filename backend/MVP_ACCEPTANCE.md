# BID OWL BASIC MVP — 실제 등록기 경로 수용 기준

## 우선순위

**BASIC MVP를 먼저 실제로 작동시키고 검증한다.** 기존 BASIC 기능을 모두 연결한 뒤 부족한 기능을 원래 설계와 비교해 채운다. PRO API, PREMIUM AI, 시각 디자인 개선은 보류한다. 이 문서는 사용자가 보유한 실제 입찰 데이터가 아니라 GitHub에 포함된 합성 CSV로 확인하는 개발 계약이다.

## MVP 한 번의 사용 흐름

1. **공고 CSV 전체 검증**: `import_local.prepare_import`. 샘플 DEMO- 출처를 실제 운영 DB에 등록할 수 없다. 사전 검증만 하는 미리보기는 DB를 생성하지 않는다.
2. **회사 정보 등록**: `CompanyProfile`의 소재지·업종·면허·인력·실적. 누락된 정보는 임의로 자격 충족으로 처리하지 않는다.
3. **명시적 저장·자격 판정**: `apply_import`는 최초 DB 생성 또는 기존 DB 백업 후 공고·회사·PASS/FAIL/UNKNOWN 판정과 증거 스냅샷을 로컬 SQLite에 저장한다. 사용자가 실제 GUI에서 확인/승인해야 저장한다.
4. **조회·상세 근거**: `viewer.open_database`에서 로컬 SQLite를 오직 읽기 전용으로 열고 `query_bids`, `query_detail`, `query_profile`을 통해 방금 등록한 공고·평가 ID·조건별 근거를 확인한다.
5. **Excel 보고서 다운로드**: 저장된 assessment ID를 `report_existing.export_existing`으로 다시 평가/수정 없이 XLSX 출력. 생성된 ZIP 패키지 및 내부 OOXML을 검사한다. 조회 화면의 기존 저장본 Excel 다운로드 API도 별도 구형 E2E 검사에서 검증한다. PDF는 한글 폰트와 선택적 ReportLab 설치가 필요하므로 `--require-pdf`를 사용할 때만 엄격한 PDF 출력을 검사한다.
6. **재등록·백업 검증**: 같은 CSV/회사를 다시 등록해 기존 판정 2건을 재사용하고 새 평가가 생기지 않는지 확인한다. 기존 DB 백업이 존재하고 원본 보고서가 바뀌지 않는지 점검한다.

## 개발판 실행기

`python backend/mvp_smoke.py`는 합성 데이터를 운영용 입력 형식으로 안전하게 재구성해 `TemporaryDirectory`에서 위 흐름을 검사한다. 실제 고객 경로나 기본 프로그램 DB를 열지 않는다. `--require-pdf` 옵션은 환경에 한국어 글꼴/ReportLab이 없으면 실패하고, 이를 PDF 통과로 가장하지 않는다.

`backend/qa_runner.py`와 `backend/verify_local.ps1`에서 실행하는 종합 QA도 기존 `smoke_local.run_smoke`와 새 `mvp_smoke.run_mvp_smoke`가 모두 성공해야 `synthetic_smoke=PASS`가 된다. 최소 한 개 이상의 Python 테스트가 실제로 실행되지 않았으면 전체 QA PASS가 불가능하다. 실패 시 실제 `qa_results` JSON과 예외 요약을 남긴다.

## 현재 완료·미완료 구분

- GitHub 개발 브랜치에 **새 실제 등록기 E2E 실행기**와 QA 연동·단위 테스트가 소스 형태로 추가됐다. 이것은 실행/합격을 뜻하지 않는다.
- 비공개 GitHub 전체 Python 테스트 및 새 E2E를 사용자 Windows에서 직접 실행해 **PASS 결과를 확보하지 않았다**. 기존 Windows 137개 테스트에서 18개 `WinError32` 임시 파일 정리 오류가 있었고 수정 여부는 아직 재확인되지 않았다.
- Tkinter 원클릭 GUI의 실제 화면·브라우저 상호작용·한국어 PDF 렌더링·Excel 실기기 열기·10,000건 성능·설치 프로그램은 출시 전 검증 대상이다.
- BASIC MVP가 개발 코드상 연결됐다는 사실과 **판매 준비 완료**는 다른 상태다. 자동 검증에서 `BASIC_MVP_SYNTHETIC_E2E_PASS` 결과가 실제로 생성된 경우에만 실행 합격으로 표시한다.

## 다음 개발 단계

1. 실제 소스 전체 E2E/회귀 테스트를 실행할 수 있는 안전하고 승인된 환경 확보(반복적인 사용자 수동 설치·ZIP 작업 요구 금지), 런타임 오류 수정.
2. CLI/GUI 실제 사용자 등록 이후 보고서 접근성을 포함한 BASIC 첫 사용 시나리오 개선. 프론트엔드 재디자인 금지.
3. 모든 BASIC 수용 기준 통과 후에만 배포/설치 파일, PRO, PREMIUM 순차 진행.

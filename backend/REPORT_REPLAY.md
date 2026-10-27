## P2-29 — 저장된 판정 여러 건 다시 보고서 출력 (실제 구현)

GUI 또는 원클릭 CSV 가져오기 도중 일부 보고서 생성이 실패한 경우 **CSV/회사 정보를 재등록하지 않고** 기존 평가 ID만 사용해 일괄 재출력할 수 있습니다. 구현 파일은 `backend/report_batch.py`입니다. 기존 `report_existing.py`의 읽기 전용 출력 코어를 그대로 사용합니다.

```powershell
cd backend
# 기본 미리보기: 기존 SQLite도 보고서 파일도 수정하지 않음
python report_batch.py --db "C:\data\bidowl.sqlite3" --assessment-ids 1,2 --output "C:\data\new-reports"
# 미리보기/출력 충돌 확인 후 실제 Excel 저장
python report_batch.py --db "C:\data\bidowl.sqlite3" --assessment-ids 1,2 --output "C:\data\new-reports" --format xlsx --apply
# 환경에 한국어 TTF/ReportLab 준비된 경우
python report_batch.py --db "C:\data\bidowl.sqlite3" --assessment-ids 3,4 --output "C:\data\other-reports" --format both --apply
```

- 평가 ID는 `import_local.py` 성공 JSON의 `assessments[].assessment_id`와 GUI의 부분 실패 시 안내되는 명령을 사용합니다. 출력이 완료된 평가 ID는 제외하고 **실패한 것만** 재출력하면 기존 파일 충돌을 피할 수 있습니다.
- 기본은 `PREVIEW_NO_WRITE`: 읽기 전용 SQLite로 최대 200개 저장된 ID 존재 여부와 출력 파일 경로 충돌을 확인합니다. `--apply` 없이는 폴더도 생성하지 않습니다. 존재하지 않는 ID, 중복·음수·숫자 이외 식별자는 거부합니다.
- `--apply`는 선택한 기존 `assessment_id`의 불변 스냅샷에서 새 XLSX/PDF를 기록합니다. **기존 SQLite를 변경하거나 재평가하지 않습니다.** 기존 출력 파일이 있으면 전체 일괄 작업 시작 전에 거부하고, 실행 도중 파일이 생겨도 개별 `xb` 안전 생성으로 덮어쓰지 않습니다.
- 두 번째 등 일부 보고서에서 실패하면 `REPORT_BATCH_PARTIAL` 및 성공한 평가 ID/파일 경로, 실패 ID를 반환하며 종료코드 2. 성공한 파일은 보존합니다. 재시도 시 **다른 새 폴더**와 실패한 ID만 사용하세요.
- `pdf/both` 형식은 한글 TTF와 ReportLab 필요조건을 모든 출력 전에 검사합니다. 데이터는 PC 밖으로 전송하지 않습니다.
- `backend/tests/test_report_batch.py`에 SQLite 합성 보고서 8개 통합 회귀 테스트를 작성했지만 사설 전체 저장소의 실제 테스트 통과는 아직 확보되지 않았습니다. 독립 환경에서 실제 `report_batch.py`와 SQLite mock export를 연결한 축소 검사 7/7 PASS만 확보했습니다. 이는 실제 전체 코드의 수용 합격이 아닙니다.

---

# P2-05 Saved report re-export and local synthetic verification

Use only on a local copy of BID OWL with an existing schema-v1 SQLite database.

From backend, re-export a prior saved assessment without re-importing/re-evaluating or writing to the source DB:

    python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./replayed_reports --format both

This opens SQLite read-only; it uses the original saved profile/bid versions and evidence. Historical PASS/FAIL is not a new/current legal eligibility result. Existing report output paths are not overwritten. For machines without ReportLab/Korean TTF use --format xlsx.

The detail drawer displays the matching assessment ID and local command. The browser cannot mutate DB data.

For a real end-to-end synthetic check (all files go into a new disposable temporary directory):

    python smoke_local.py

The runner imports fixtures/sample_bids.csv and fixtures/sample_profile.json, tests XLSX and localhost HTTP list/detail/favorites/profile, re-exports a saved report, applies a versioned profile revision with a backup, re-assesses, and verifies the old assessment and backup. It does not use customer data, official APIs, external services or PDFs.

Full Python regression:

    python -m unittest discover -s tests -v

Current GitHub test inventory should include 116 prior methods plus 6 report re-export and 1 synthetic smoke = 123. **These 123 have not yet been run in an authenticated full checkout**. The new source/tests are committed but runtime and Windows/native browser and PDF validation remain pending.

## P2-06 failure recovery and first-use onboarding

Saved report replay is now more conservative on output failure:
- The XLSX writer cleans up a newly created partial archive if ZIP/XML writing fails, while never unlinking an already existing report.
- If the PDF renderer fails after a completed XLSX in a `--format both` replay, the completed sibling XLSX is removed; the PDF writer separately cleans up its own partial output. This is best-effort cleanup, not a general two-file atomic transaction against power loss or abnormal process death.
- Added tests for interrupted second worksheet, second-format failure and pre-existing PDF preservation. These tests are committed but the full checkout has not been run.

The BASIC interface now supports "새 회사 프로필 만들기" (download validated JSON) and existing profile editing. Both lead to a local CLI command; database writes require explicit `--create --apply --backup` and preflight. The browser itself remains read-only toward SQLite.

Windows 11 authorized private checkout verification from backend:

    powershell -ExecutionPolicy Bypass -File .\verify_local.ps1

This runs the full unittest suite, then the synthetic local end-to-end test and optional Node syntax validation. It prints a completion notice only after invoked checks return successful exit codes; it does NOT check native Excel/PDF appearance or live government bids. PowerShell script has been committed, not executed on Windows in this session.

Current GitHub source declares **126 Python test methods** in eight test files, confirmed by reading code. Do not call that 126 passing tests until `verify_local.ps1` or `python -m unittest discover -s tests -v` actually completes against an authenticated checkout. No new app deployment or GitHub main changes.


## P2-07 direct local Excel download (source implemented)

With `python viewer.py --db ./demo.sqlite3 --port 8765` running on 127.0.0.1, open a previously assessed bid's details. The "Excel (.xlsx) 직접 다운로드" link now calls:

    GET http://127.0.0.1:8765/api/report?assessment_id=1

This is a **read-only** path: it accepts only a positive, bounded persisted assessment ID, opens the local DB in `mode=ro` with `PRAGMA query_only=ON`, reconstructs the immutable original version/evidence, writes the generated XLSX only into a self-cleaning temporary directory, then responds with XLSX binary and a fixed Content-Disposition attachment filename. The response has `Cache-Control: no-store`, `nosniff` and existing localhost Host/Origin checks. When Fetch Metadata is present, explicit cross-site requests are refused; browser same-origin downloads work through a normal link. Maximum generated file size is 16 MiB. No arbitrary download directory path or file upload is accepted from HTTP, and no permanent report is created by this new route.

PDF still uses the existing explicit CLI `report_existing.py --format pdf`, because its local ReportLab/Korean-font dependency and browser handling have not been validated. The detail drawer retains that CLI example.

New regression methods in `tests/test_report_existing.py` test actual synthesized XLSX byte signatures, ZIP contents, DB read-only enforcement, localhost HTTP attachment headers, nonexistent IDs, invalid parameters and cross-site/host rejection. `smoke_local.py` now exercises HTTP attachment bytes too. All source/tests are committed but full Python execution in an exact private checkout is still pending. Do not call the number of declared test definitions PASS.

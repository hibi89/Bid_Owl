## P2-27 — Windows GUI에서 Excel/PDF 출력까지 연결

이제 `START_BID_OWL_IMPORT.cmd`의 Tkinter 등록기에 **등록 후 보고서 생성** 선택과 `xlsx`/`pdf`/`both` 형식 선택이 있다(기본 체크/Excel). CSV 및 회사 정보를 사전 검사한 뒤 출력 폴더를 선택하며, PDF 또는 둘 다 선택 시 ReportLab/한국어 글꼴 요구사항을 **DB 저장 전에** 확인한다. 확인창에 대상 DB/백업/출력 폴더가 표시된다.

사용자가 승인을 누르면 기존과 동일하게 안전한 DB 등록·평가/백업을 수행하고, **저장된 assessment ID**로 `report_existing` 읽기 전용 출력을 수행한다. 출력 중 실패해도 DB 저장을 취소·되돌리지 않는다. 이미 생성된 보고서 수와 원본 DB/백업 위치를 경고하며, 새 폴더로 필요한 보고서만 재출력할 수 있다. 기존 파일을 자동 덮어쓰지 않는다. 보고서 체크를 해제하면 기존처럼 등록·조회만 실행한다. Python GUI/Windows 실행 테스트는 아직 미검증이며 출시 완료 판정 아님.

---

## P2-26 — 등록과 Excel/PDF 내보내기를 한 번에 실행 (BASIC MVP)

기존 실제 공고 등록기 `import_local.py`에 선택적 `--export-dir`를 추가했습니다. CLI에서 **명시적 `--apply`를 지정한 경우에만** 저장 후 동일 공고의 확정된 `assessment_id`로 보고서를 내보냅니다. 과거 판정을 재사용하면 기존 동일 평가 ID를 사용하며 다시 평가하거나 과거 보고서 파일을 덮어쓰지 않습니다.

```powershell
cd backend
python import_local.py --csv "C:\\data\\bids.csv" --profile "C:\\data\\company.json" --source-id LOCAL-2026 --apply --export-dir "C:\\data\\reports"
# PDF 폰트/ReportLab 환경이 확인되었을 때에만 양식 둘 다:
python import_local.py --csv "C:\\data\\bids.csv" --profile "C:\\data\\company.json" --source-id LOCAL-2026 --apply --export-dir "C:\\data\\new-reports" --report-format both
```

`--export-dir`가 없으면 이전처럼 **등록만** 합니다. `--report-format`은 `xlsx`(기본)/`pdf`/`both` 중 하나입니다. PDF를 요청했는데 한글 글꼴이나 ReportLab이 없으면 **저장 전에** 실패합니다.

성공 결과 `IMPORTED_AND_EXPORTED`에는 `assessments` (공고번호·평가 ID·PASS/FAIL/UNKNOWN·재사용 여부)와 `reports` (동일 ID의 로컬 생성 파일) 배열이 들어갑니다. 등록과 평가가 먼저 확정된 뒤 **보고서 생성만 실패**했으면 `IMPORTED_EXPORT_FAILED`로 종료하고 데이터 저장은 성공했음을 명시합니다. 기존 원본 DB·백업은 그대로 유지되며 완료된 보고서가 있다면 경로를 반환합니다. 덮어쓰기/자동 롤백을 시도하지 않으므로 사용자는 다른 출력 폴더를 지정해 기존 평가 ID 보고서를 `report_existing.py`로 다시 내보낼 수 있습니다.

**MVP 자동 검사:** `backend/mvp_smoke.py`가 동일한 등록+보고서 원클릭 CLI 경로로 합성 공고 2건을 추가 검사하도록 확장되었습니다. 전체 제품 Python 테스트/Windows 실사용 합격 기록은 아직 없습니다. 공시 라이트닝(KIC) 재사용은 BASIC MVP 검증 후 **별도 공시 원본→정규화 어댑터**로 진행하며 현재 입찰 판정이 해외 공시 규칙까지 지원한다는 주장은 하지 않습니다.

---

# BID OWL P2-14 — 실제 CSV + 회사 정보 로컬 등록

이 문서는 상용 사용자 DB용 **등록 작업**입니다. 가상 공고만 사용하는 `DEMO.md`와 별도이며, 실제 사용자 파일을 GitHub·외부 서버·모델 API로 전송하지 않습니다. Python 3.11 이상의 Windows 로컬 PC용으로 설계했으며 이 단계는 개발판으로, 실제 Windows 11 화면과 전체 회귀 테스트 통과는 아직 미확인입니다.

## 원클릭 등록 GUI

GitHub 개발 브랜치 압축을 푼 뒤 저장소 최상위의 **`START_BID_OWL_IMPORT.cmd`**를 더블클릭합니다. `backend/START_IMPORT.cmd`도 동일합니다. Python 기본 설치에 Tkinter GUI 구성요소가 필요합니다. 공공기관 API, PDF 글꼴, ReportLab 및 구독 서비스는 필요하지 않습니다.

1. 로컬 CSV 선택. 사용자가 직접 준비한 **실제 공고 CSV**만 사용합니다. 샘플 `fixtures/sample_bids.csv`의 `DEMO_ONLY` 공고를 실제 DB에 등록하는 것은 차단됩니다.
2. 출처 ID 지정. 예: `LOCAL-2026-OCT`. 공고번호는 출처 ID와 함께 식별하므로 같은 출처의 재가져오기는 중복 행 대신 버전 비교합니다.
3. 회사 프로필 ID, 소재지, 업종, 면허, 직원 수, 실적 금액 기입. 등록하기 전에 만들어둔 JSON 프로필은 **기존 회사 JSON 불러오기** 버튼으로 입력 폼에 채울 수 있습니다.
4. **검증 후 백업·가져오기**를 누르면 먼저 CSV 전체를 읽고 데이터 스키마·회사 정보·기존 DB/프로필을 **읽기 전용으로** 검사합니다. 이때 DB에 기록하지 않습니다.
5. 공고 개수, 출처 ID, 회사 ID, 로컬 DB 위치, 기존 DB의 백업 여부를 확인한 후 확인 창에서 **명시적으로 승인**해야 저장합니다. 기존 DB는 첫 수정 전에 `.../BID_OWL/backups/<db>_<UTC>_<random>.sqlite3`에 **덮어쓰지 않는 SQLite 일관 백업**을 만듭니다. 신규 DB에는 이전 데이터가 없으므로 백업이 없습니다.
6. 로컬 규칙 판정 결과 PASS/FAIL/UNKNOWN 수를 보여줍니다. 원하는 경우 기존 읽기 전용 `127.0.0.1` 공고 조회 화면을 실행합니다. 브라우저를 열었다면 해당 PowerShell/명령 창의 Ctrl+C로 종료할 수 있습니다.

회사 정보에서 **빈칸은 정보 없음(unknown)**으로 저장하며, 임의로 0건/면허 없음/자격충족으로 처리하지 않습니다. 이미 저장된 **동일 프로필 ID에 다른 내용**이 입력되면 가져오기를 중단하고 `profile_workflow.py`의 버전 확인·백업 필수 편집 절차를 사용하도록 안내합니다. 기존 회사 프로필을 묵시적으로 갱신하지 않습니다.

## 자동화·QA용 CLI — 기본은 저장하지 않는 미리보기

```powershell
cd backend

python import_local.py --csv "C:\data\bids.csv" --profile "C:\data\company.json" --source-id LOCAL-OCT --db "C:\data\bidowl.sqlite3"

# 사전 검토 후 저장하기로 결정했을 때만
python import_local.py --csv "C:\data\bids.csv" --profile "C:\data\company.json" --source-id LOCAL-OCT --db "C:\data\bidowl.sqlite3" --apply
```

`--db`를 빼면 운영체제 로컬 애플리케이션 폴더 아래의 BID OWL 기본 DB를 사용합니다. CLI에서 `--apply`를 생략하면 `PREVIEW_NO_WRITE` JSON만 출력하며 DB를 만들지 않습니다. 프로필 JSON은 기존 `profile_workflow.load_profile_file`로 검증하고, GUI 작성 프로필도 동일한 300자 필드/목록 제한을 적용합니다.

CSV 입력 계약(UTF-8/UTF-8-SIG, 최대 10 MiB·10,000행):
`bid_no,title,agency,category,bid_deadline,budget,requirements` 필수,
`source_ref,data_as_of` 선택. 날짜·금액·출처·규칙의 구체 형식은 [README.md](README.md)의 입력 계약을 참고하세요. 입력 전체가 검증되지 않으면 저장하지 않습니다. 데모용 회사 `SYNTHETIC-` 프로필, `DEMO-` 공고, `DEMO_ONLY` 출처 및 전용 `BIDOWL_SYNTHETIC_DEMO` 출처 ID를 사용자 DB에 등록하지 않습니다.

## 백업·실패·보안 제한

- **기존 DB 수정 전 백업** 및 프로필 버전 조건부 저장을 지원합니다. 백업 파일을 자동 덮어쓰거나 자동 복구하지 않습니다. 손상 또는 중단 시 원본과 백업을 확인한 후 수동 복원하세요.
- 공고 가져오기·회사 프로필 저장·각 공고 평가가 각각 DB 트랜잭션을 사용합니다. **전체 등록은 단일 원자 트랜잭션이 아닙니다**. 중간 실패 시 `IMPORT_PARTIAL_OR_UNCERTAIN` 오류와 백업 정보를 반환합니다. 신규 DB에는 이전 백업이 없으므로 아직 완료되지 않은 DB가 남을 수 있습니다.
- 미리보기 후 CSV 변경을 SHA-256으로 재검사하고, 기존 DB/프로필 변경도 읽기 전용으로 다시 점검합니다. 신규 DB는 OS의 배타적 파일 생성(\`xb\`)으로 경합 중 다른 프로세스가 만든 파일을 덮어쓰지 않도록 보호합니다. 동시 외부 쓰기까지 완전하게 격리하는 교차 프로세스 락을 제공하지는 않습니다.
- GUI는 운영체제 파일 선택·입력 창(Tkinter)을 쓰며 브라우저에 DB 쓰기 엔드포인트를 추가하지 않습니다. 완료 후 공고 뷰어는 오직 `127.0.0.1`에 바인딩되고 SQLite는 읽기 전용으로 엽니다.
- 이 단계는 CSV 전체 가져오기 및 검토 스냅샷 생성에 집중합니다. 기존 PDF/XLSX는 별도 기존 명령 및 읽기 전용 보고서 기능을 사용합니다. Windows 설치 파일·Excel 원본 출력·실제 대량 조회 성능·면허 법률 판정 정확도는 검증 완료로 주장하지 않습니다.

## 검증 상태

`tests/test_import_local.py`에 미리보기 무변경, 신규 저장, 기존 DB 백업과 재등록, 불일치 프로필 차단, 잘못된 CSV/데모/기존 타사 DB 차단, 파일 변경 경쟁, 프로필 변경, 중단 시 백업 보존, 미확인 입력, CLI 미리보기/명시적 적용, 실행기 경로 및 신규 DB 경로 경합 보호 등 **18개 테스트 정의**를 추가했습니다. 테스트 함수 정의와 실행 통과는 별개입니다. 전체 Windows/Python 실제 통합 실행은 검증 전입니다.

## P2-15 — 동일 공고 재등록 시 판정 재사용

CSV를 다시 가져올 때 공고 데이터와 회사 정보가 이전과 같으면, 마지막으로 저장된 **유효한 판정 스냅샷**을 재사용합니다. 다음 조건이 **모두** 같을 때만 재사용합니다.

- 동일한 `source_id + bid_no + profile_id`에 마지막으로 기록된 판정
- 현재 공고 버전과 스냅샷 공고 버전 일치
- 현재 회사 프로필 버전과 스냅샷 프로필 버전 일치
- **현재 시각 기준 마감 상태**와 스냅샷의 `is_expired` 값 일치

따라서 공고 내용이나 회사 버전이 바뀌었거나, 시간 경과로 접수 마감 상태가 바뀌면 재평가합니다. 기존 평가의 불변 스냅샷을 수정하거나 과거 평가일시를 최신으로 속이지 않습니다. 프로필 버전이 가져오기 도중 변경되면 중단하고 백업을 보관하며 확인을 요구합니다.

적용 응답에는 `assessments_saved`(새로 생성된 평가), `assessments_reused`(기존 저장본 재사용), `eligibility_counts`(이번에 처리한 공고 전체의 PASS/FAIL/UNKNOWN 합계)가 각각 들어갑니다. 예를 들어 2개 공고를 동일하게 재등록하면 **새 판정 0개 / 기존 판정 재사용 2개**가 예상됩니다. 이는 검사 대상 CSV의 데이터와 프로필 버전·마감 상태가 변경되지 않았을 때에만 성립합니다.

기존 DB는 재가져오기에서도 **백업 생성 후 공고 가져오기 감사 기록을 추가**하기 때문에, 판정 0개인 경우에도 백업이 생길 수 있습니다. 최초 저장 이후의 판정 스냅샷 근거는 별도로 유지됩니다. 전체 작업을 단일 트랜잭션으로 보장하지 않으며 원본 공고문 확인 의무는 변경되지 않습니다.

신규 회귀 테스트는 동일 파일 반복 등록 시 ID 유지, 한 공고만 수정했을 때 선택적 재평가, 마감 상태 불일치, 회사 프로필 버전 변경 및 작업 중 회사 버전 변경을 다룹니다. 별도의 간이 SQLite SQL 계약 검사 4건은 로컬 Python에서 통과했지만, **개발 브랜치 전체 Python 테스트 실행과 Windows 실사용 검증은 아직 완료되지 않았습니다.**

### 규칙 엔진을 업그레이드한 경우

변경되지 않은 공고라도 규칙 판정 알고리즘 자체가 수정된 뒤에는 기존 스냅샷을 재사용하는 것이 적절하지 않을 수 있습니다. 이를 위해 GUI의 **‘저장된 판정도 모두 재평가’** 체크박스와 CLI `--force-reassess`를 제공하며, 이를 선택하면 기존 버전의 판정이 있더라도 이번 CSV 전체에 대해 새 평가 스냅샷을 추가합니다. 과거 판정은 삭제·덮어쓰지 않습니다.

```powershell
python import_local.py --csv "C:\data\bids.csv" --profile "C:\data\company.json" --source-id LOCAL-OCT --db "C:\data\bidowl.sqlite3" --apply --force-reassess
```

**P2-16 변경:** 규칙 판정·데이터 스키마·회사 정보·저장 엔진 코드를 SHA-256으로 식별합니다. 기존 평가 지문이 없거나 현재 엔진 지문과 다르면 **자동 재평가**하며, 이전 PASS는 로컬 화면에서 재평가 전까지 UNKNOWN으로 표시합니다. 위 수동 `--force-reassess`는 동일한 엔진으로도 강제 재확인하려는 별도 선택지로 계속 유지합니다. 자세한 보존·마이그레이션 제한은 [ENGINE_POLICY.md](ENGINE_POLICY.md) 참조.


## P2-16 규칙 엔진 지문 기반 자동 무효화

- `assessment_engine_provenance` 메타 테이블에 평가별 `engine_hash`를 저장합니다. 새 DB는 초기 생성 시 포함합니다. 기존 v1 DB는 **별도 DB 백업 이후 첫 적용 단계에서만** 테이블을 추가하며 과거 판정 자체를 덮어쓰지 않습니다.
- 소스 파일 `eligibility.py`, `schema.py`, `profile.py`, `store.py`의 내용을 해시합니다. 규칙 코드 변경은 다음 가져오기에서 일치하지 않는 판정을 자동으로 재평가합니다.
- 메타 테이블이 없거나 해시가 없는 오래된 평가의 화면상 현재 상태는 `UNKNOWN`이며, 별도 `snapshot_status`에는 과거 판정을 보존합니다. 현 버전과 지문이 동일하고 공고·프로필 버전과 마감 상태가 맞아야 재사용합니다.
- CLI 이외 기존 `profile_workflow.py`의 회사 편집·재평가도 **백업 성공 후** 메타 테이블을 추가합니다. 구형 `cli.py`에서 메타 테이블 없이 평가한 결과는 출처가 미확인으로 남아 새 등록기를 통한 재평가가 필요할 수 있습니다.
- 패키징에서 정책 소스가 빠지면 새 평가 기록을 차단하고, 조회 화면은 기존 PASS를 UNKNOWN으로 처리합니다. 출시용 단일 실행 파일은 소스 리소스 포함 또는 검증된 정책 매니페스트 설계가 추가로 필요합니다.
- 코드/회귀 테스트가 GitHub에 구현되어 있으나 **실제 Windows 전수 통합 QA는 미실행**입니다.

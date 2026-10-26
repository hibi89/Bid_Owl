# BID OWL — P2-18 DB 파일 삭제·교체 보호 계약

이 문서는 Python + SQLite로 구성된 **로컬 개발판**의 코드 계약이다. 동시 쓰기 완전 차단이나 Windows 전체 QA 완료를 뜻하지 않는다.

## 문제

기존 `BidOwlStore(db_path)`는 SQLite 기본 연결 방식으로 파일이 없으면 **새 DB를 자동 생성**한다. 사용자 파일을 읽기 전용으로 검증한 직후 다른 프로그램이 파일을 지우거나 교체하면, 이후 기존 파일을 열려던 호출이 비어 있는 DB를 새로 만들 수 있었다. 새 파일이 유효한 다른 회사 DB로 교체됐을 때도 앞서 검사한 내용과 달라질 수 있었다.

## P2-18 적용

- `BidOwlStore(path, must_exist=True)`: `file://...?...mode=rw` 연결 사용. 대상 DB가 없으면 **생성하지 않고 실패**한다. 존재하더라도 BID OWL v1 스키마가 아니면 자동 초기화하지 않고 거부한다. 기본 인자 없는 기존 신규 DB 생성 흐름은 호환성을 위해 유지한다.
- `database_file_identity(path)`: OS `stat`의 디바이스 번호·inode·파일 크기·수정 시각(ns)을 묶어 읽기 전용 검사와 실제 쓰기 오픈 사이에 비교한다. `expected_identity` 인자로 전달하여 연결 전·연결 직후 변경을 모두 검사하고 충돌 시 중단한다.
- 새 DB는 기존 `open('xb')` 독점 파일 예약 뒤 이 **동일한 파일 식별값**을 사용해 `mode=rw`로 초기화한다. 다른 프로세스가 그 파일을 삭제하면 새 파일을 만들지 않으며 교체하면 식별값 불일치로 실패한다.
- 사용 경로: `import_local.py` 미리보기→저장, `cli.py` 구형 보고서 겸 CSV 등록, `profile_workflow.py` 기존 회사 편집. 조회 전용 `viewer.py`는 기존 `mode=ro`를 유지한다.
- 기존 DB는 스키마 변경·CSV 등록·재평가 **전** 비덮어쓰기 SQLite 백업을 만든다. 파일 분실·변경이 발견되면 **백업이나 DB에 새로운 내용을 쓰기 전에** 실패하도록 순서를 유지한다.

## 한계와 진단

이 방법은 파일 경로 식별값을 비교하는 **best-effort TOCTOU 보호**다. 교체 직후 inode 재사용, 외부 프로세스의 유효 DB에 대한 동시 수정, 연결 오픈 이후의 경로 리네임, SMB/네트워크 파일시스템의 `stat` 동작까지 완전하게 배제하는 파일 락은 아니다. 외부 프로세스가 쓰기를 수행할 수 있는 고객 DB는 단일 로컬 프로세스 정책·잠금·복구 검증이 추가로 필요하다.

- 사전 검사와 저장 사이 삭제: `FileNotFoundError` 또는 SQLite `OperationalError`. 원래 DB가 없어졌다면 **자동 재생성하지 않는다**.
- 기존 DB가 다른 파일로 바뀜: `ValueError` (식별값 변경), 기록을 시도하지 않는다.
- 파일 자체가 빈 파일이나 다른 SQLite: `SchemaVersionError` 또는 데이터베이스 오류; 타사 DB를 BID OWL로 재초기화하지 않는다.
- 파일 정상, 수정 작업 중 예외: 기존 백업 보존, `IMPORT_PARTIAL_OR_UNCERTAIN` / `CLI_PARTIAL_OR_UNCERTAIN` 같은 명시적인 후속 점검 신호. 다중 공고 전체를 하나의 단일 트랜잭션으로 보장하지 않는다.

## 검증 현황

`tests/test_store.py`, `test_import_local.py`, `test_cli_safe.py`, `test_profile_workflow.py`에 합성 SQLite 삭제·교체·빈 파일·이미 예약된 신규 DB 경계 테스트를 추가했다. 별도 Python 임시 폴더에서 실제 SQLite `mode=rw` 비생성, 빈 DB 스키마 버전, `os.replace`의 파일 식별 변경을 **4/4 확인**했다. 이는 GitHub 전체 Python 테스트 실행 결과가 아니며, Windows `WinError 32`의 해결을 검증했다는 의미도 아니다. 출시 전 동일 드라이브/OneDrive/윈도우 잠금 상황에서 통합 테스트가 필요하다.

"""BID OWL BASIC: deliberate, local-only CSV + company onboarding.

CLI dry-run by default; --apply explicitly permits writes. The optional
Tkinter desktop wizard also shows a preflight summary and asks for consent.
No HTTP mutation endpoint, network API, customer uploads or PDF dependency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import sqlite3
import sys
import webbrowser
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from bidowl import BidOwlStore, CompanyProfile, CSVImportError, parse_csv
from bidowl.engine_identity import engine_fingerprint
from bidowl.schema import MAX_CSV_BYTES
from bidowl.store import database_file_identity, default_database_path
from profile_workflow import load_profile_file
from report_existing import export_existing
from bidowl.report import check_pdf_support
from viewer import make_server, open_database

RESERVED_DEMO_SOURCE = "BIDOWL_SYNTHETIC_DEMO"


@dataclass(frozen=True)
class ImportPlan:
    db_path: Path
    source_id: str
    csv_path: Path
    csv_sha256: str
    bids: tuple
    profile: CompanyProfile
    existing_db: bool
    existing_profile_version: int
    profile_action: str
    db_identity: tuple[int, int, int, int] | None = None


def _check_source_id(value: str) -> str:
    if (not isinstance(value, str) or not value.strip()
            or len(value) > 300 or value != value.strip()):
        raise ValueError("Source ID must contain 1..300 characters with no outer whitespace")
    if value == RESERVED_DEMO_SOURCE:
        raise ValueError("Reserved synthetic-demo source cannot be imported as customer data")
    return value


def _check_real_inputs(bids: tuple, profile: CompanyProfile) -> None:
    # Match the existing profile_workflow local JSON file boundary for
    # GUI-built profiles too; the dataclass itself is intentionally permissive.
    if len(profile.profile_id) > 300 or (
        profile.region is not None and len(profile.region) > 300
    ):
        raise ValueError("Profile ID and region must not exceed 300 characters")
    for values in (profile.categories, profile.licenses):
        if values is not None and (
            len(values) > 100 or any(len(value) > 300 for value in values)
        ):
            raise ValueError("Profile lists are limited to 100 entries of 300 characters")
    if not bids:
        raise ValueError("CSV contains no valid tenders")
    if profile.profile_id.startswith("SYNTHETIC-"):
        raise ValueError("Synthetic demo company profiles cannot be used for real import")
    if any(b.source_ref == "DEMO_ONLY" or b.bid_no.startswith("DEMO-") for b in bids):
        raise ValueError("Packaged synthetic demo tenders are not accepted by real importer")


def _existing_db_state(db_path: Path, profile: CompanyProfile) -> tuple[bool, int, str]:
    if not db_path.exists():
        return False, 0, "CREATE"
    if not db_path.is_file():
        raise ValueError("Database destination is not a regular file")
    with closing(open_database(db_path)) as conn:
        # Preflight against the full schema before opening a write-capable store.
        required = {"profiles", "profile_versions", "bids", "bid_versions",
                    "import_runs", "assessments", "rule_assessments"}
        present = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if not required <= present:
            raise ValueError("Not a complete BID OWL database")
        row = conn.execute(
            "SELECT latest_version FROM profiles WHERE profile_id=?", (profile.profile_id,)
        ).fetchone()
        if row is None:
            return True, 0, "CREATE"
        old = conn.execute(
            "SELECT payload FROM profile_versions WHERE profile_id=? AND version=?",
            (profile.profile_id, row["latest_version"]),
        ).fetchone()
        if old is None:
            raise ValueError("Company profile history is incomplete")
        saved = CompanyProfile.from_mapping(json.loads(old["payload"]))
        if saved != profile:
            raise ValueError(
                "Existing company profile differs. Apply edits via profile_workflow.py "
                "with expected-version and an explicit backup first."
            )
        return True, int(row["latest_version"]), "KEEP"


def prepare_import(
    *,
    csv_path: str | Path,
    profile: CompanyProfile,
    source_id: str,
    db_path: str | Path | None = None,
) -> ImportPlan:
    """Completely validate input and existing DB in read-only mode; no writes."""
    if not isinstance(profile, CompanyProfile):
        raise TypeError("profile must be a CompanyProfile")
    source_id = _check_source_id(source_id)
    source = Path(csv_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"CSV file not found: {source}")
    if source.stat().st_size > MAX_CSV_BYTES:
        raise ValueError(f"CSV exceeds {MAX_CSV_BYTES} bytes")
    csv_bytes = source.read_bytes()
    if len(csv_bytes) > MAX_CSV_BYTES:
        raise ValueError(f"CSV exceeds {MAX_CSV_BYTES} bytes")
    bids = parse_csv(csv_bytes).require_valid()
    _check_real_inputs(bids, profile)
    destination = Path(db_path).expanduser().resolve() if db_path is not None else default_database_path()
    initial_identity = database_file_identity(destination) if destination.exists() else None
    present, version, action = _existing_db_state(destination, profile)
    after_identity = database_file_identity(destination) if destination.exists() else None
    if initial_identity != after_identity or present != (initial_identity is not None):
        raise ValueError("Database changed while preparing preview; retry")
    return ImportPlan(
        db_path=destination, source_id=source_id, csv_path=source,
        csv_sha256=hashlib.sha256(csv_bytes).hexdigest(), bids=tuple(bids),
        profile=profile, existing_db=present,
        existing_profile_version=version, profile_action=action,
        db_identity=initial_identity,
    )


def plan_summary(plan: ImportPlan) -> dict:
    return {
        "status": "PREVIEW_NO_WRITE",
        "source_id": plan.source_id,
        "csv_path": str(plan.csv_path),
        "database": str(plan.db_path),
        "database_exists": plan.existing_db,
        "backup_required": plan.existing_db,
        "bid_count": len(plan.bids),
        "company_id": plan.profile.profile_id,
        "profile_action": plan.profile_action,
        "notice": "Eligibility remains subject to source review; nothing was written.",
    }


def _new_backup_path(db_path: Path) -> Path:
    label = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return db_path.parent / "backups" / (
        f"{db_path.stem}_{label}_{secrets.token_hex(5)}.sqlite3"
    )


def _reusable_assessment_status(
    store: BidOwlStore, *, source_id: str, bid_no: str,
    profile_id: str, profile_version: int, is_expired: bool,
    engine_hash: str,
) -> tuple[int, str] | None:
    """Reuse only a snapshot matching both revisions and today's expiry.

    A bid can pass its deadline without a data revision. An assessment from
    before that boundary must be regenerated, not silently reused.
    """
    row = store.db.execute("""
        SELECT b.latest_version,
               p.latest_version AS current_profile_version,
               a.id AS assessment_id, a.bid_version, a.profile_version,
               a.status, a.is_expired, ep.engine_hash
        FROM bids b
        JOIN profiles p ON p.profile_id = ?
        LEFT JOIN assessments a ON a.id = (
            SELECT x.id FROM assessments x
            WHERE x.source_id = b.source_id AND x.bid_no = b.bid_no
              AND x.profile_id = ?
            ORDER BY x.id DESC LIMIT 1
        )
        LEFT JOIN assessment_engine_provenance ep ON ep.assessment_id=a.id
        WHERE b.source_id = ? AND b.bid_no = ?
    """, (profile_id, profile_id, source_id, bid_no)).fetchone()
    if row is not None and row["current_profile_version"] != profile_version:
        raise ValueError("Company profile changed while importing; retry")
    if (row is not None and row["status"] in ("PASS", "FAIL", "UNKNOWN")
            and row["bid_version"] == row["latest_version"]
            and row["profile_version"] == profile_version
            and row["engine_hash"] == engine_hash
            and bool(row["is_expired"]) == is_expired):
        return int(row["assessment_id"]), str(row["status"])
    return None


def apply_import(plan: ImportPlan, *, force_reassess: bool = False) -> dict:
    """Explicitly called only after review/consent. Fail closed on changed DB.

    A backup protects an existing DB before the first persistent mutation.
    Multi-stage import/profile/assess writes are NOT a single transaction:
    on any post-backup failure, report possible partial writes and keep backup.
    """
    if not isinstance(plan, ImportPlan):
        raise TypeError("Expected an ImportPlan from prepare_import")
    if type(force_reassess) is not bool:
        raise ValueError("force_reassess must be a boolean")
    # Fail CLOSED before any DB write if the rule-policy source resources
    # cannot be verified (e.g. a mispackaged executable).
    policy_hash = engine_fingerprint()
    # Input file may be changed after preview; require identical bytes.
    if plan.csv_path.stat().st_size > MAX_CSV_BYTES:
        raise ValueError("CSV grew beyond 10 MiB since preview")
    actual = plan.csv_path.read_bytes()
    if len(actual) > MAX_CSV_BYTES:
        raise ValueError("CSV grew beyond 10 MiB since preview")
    if hashlib.sha256(actual).hexdigest() != plan.csv_sha256:
        raise ValueError("CSV changed after preview; review it again before importing")
    current_identity = database_file_identity(plan.db_path) if plan.db_path.exists() else None
    if (current_identity is None) != (not plan.existing_db):
        raise ValueError("Database creation/deletion detected since preview; retry")
    if current_identity != plan.db_identity:
        raise ValueError("Database replaced or modified since preview; retry")
    # A second read-only preflight catches changed profile/version/schema.
    current_db, version, action = _existing_db_state(plan.db_path, plan.profile)
    if (current_db, version, action) != (
        plan.existing_db, plan.existing_profile_version, plan.profile_action
    ):
        raise ValueError("Database/profile changed since preview; retry")
    final_identity = database_file_identity(plan.db_path) if plan.db_path.exists() else None
    if final_identity != plan.db_identity:
        raise ValueError("Database changed during apply preflight; retry")
    backup = None
    started_writing = False
    # sqlite3.connect() creates absent files without exclusivity.
    # Reserve a truly new DB with O_EXCL ("xb") so a file appearing
    # between read-only preflight and open cannot be silently adopted.
    if not plan.existing_db:
        plan.db_path.parent.mkdir(parents=True, exist_ok=True)
        with plan.db_path.open("xb"):
            pass
    expected_identity = (plan.db_identity if plan.existing_db
                         else database_file_identity(plan.db_path))
    try:
        with BidOwlStore(
            plan.db_path, must_exist=plan.existing_db,
            expected_identity=expected_identity,
        ) as store:
            if plan.existing_db:
                backup = store.backup_to(_new_backup_path(plan.db_path))
            # This is an additive v1 table, never created merely by opening
            # an existing DB. Existing DB is now backed up; new DB is ours.
            started_writing = True
            store.db.execute("""
                CREATE TABLE IF NOT EXISTS assessment_engine_provenance (
                    assessment_id INTEGER PRIMARY KEY,
                    engine_hash TEXT NOT NULL CHECK(length(engine_hash) = 64),
                    FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
                )
            """)
            # Use CAS for both first-creation and already-matching profile.
            if plan.profile_action == "CREATE":
                started_writing = True
                profile_version = store.save_profile(
                    plan.profile, expected_version=0
                )
            else:
                profile_version = version
                if store.get_profile(plan.profile.profile_id) != plan.profile:
                    raise ValueError("Profile changed since preview")
            # Every imported bid version and evaluation is stored locally.
            started_writing = True
            imported = store.import_bids(
                plan.bids, source_id=plan.source_id,
                file_sha256=plan.csv_sha256,
            )
            counts = {"PASS": 0, "FAIL": 0, "UNKNOWN": 0}
            saved_assessments = 0
            reused_assessments = 0
            assessments = []
            for bid in plan.bids:
                checked_at = datetime.now(timezone.utc)
                previous_snapshot = None
                if not force_reassess:
                    previous_snapshot = _reusable_assessment_status(
                        store, source_id=plan.source_id, bid_no=bid.bid_no,
                        profile_id=plan.profile.profile_id,
                        profile_version=profile_version,
                        is_expired=bid.is_expired(checked_at),
                        engine_hash=policy_hash,
                    )
                if previous_snapshot is not None:
                    assessment_id, previous_status = previous_snapshot
                    reused_assessments += 1
                    counts[previous_status] += 1
                    assessments.append({
                        "bid_no": bid.bid_no, "assessment_id": assessment_id,
                        "status": previous_status, "reused": True,
                    })
                    continue
                assessment_id, outcome = store.assess_and_record(
                    plan.source_id, bid.bid_no, plan.profile.profile_id,
                    expected_profile_version=profile_version,
                    checked_at=checked_at,
                )
                saved_assessments += 1
                counts[outcome.status] += 1
                assessments.append({
                    "bid_no": bid.bid_no, "assessment_id": assessment_id,
                    "status": outcome.status, "reused": False,
                })
    except BaseException as exc:
        if started_writing:
            # Do not auto-restore: a concurrent write or successful earlier
            # statement may exist. Preserve the backup for manual recovery.
            raise RuntimeError(
                f"IMPORT_PARTIAL_OR_UNCERTAIN: inspect SQLite before further writes. "
                f"Backup: {backup if backup is not None else 'new DB (no older data)'}. "
                f"Cause: {type(exc).__name__}"
            ) from exc
        raise
    return {
        "status": "IMPORTED",
        "source_id": plan.source_id,
        "database": str(plan.db_path),
        "backup": str(backup) if backup else None,
        "profile_id": plan.profile.profile_id,
        "profile_version": profile_version,
        "import": {
            "inserted": imported.inserted,
            "revised": imported.revised,
            "unchanged": imported.unchanged,
        },
        "assessments_saved": saved_assessments,
        "assessments_reused": reused_assessments,
        "assessments": assessments,
        "eligibility_counts": counts,
        "notice": "Rule screening only; check the original tender before any bid.",
    }


class ReportExportError(RuntimeError):
    """The DB import succeeded, but a post-commit report export failed."""

    def __init__(self, cause: Exception, completed: list[dict]):
        super().__init__(str(cause))
        self.cause = cause
        self.completed = tuple(completed)


def export_saved_assessments(
    outcome: dict, *, db_path: Path, output_dir: Path, report_format: str = "xlsx",
) -> list[dict]:
    """Read-only export of exactly the committed assessment IDs.

    Never retry the import on an export error. Preserve paths for already
    completed files so the operator can use a new output directory safely.
    """
    if outcome.get("status") != "IMPORTED":
        raise ValueError("Only committed imports can be exported")
    if report_format not in ("xlsx", "pdf", "both"):
        raise ValueError("Unsupported report format")
    completed = []
    for assessment in outcome["assessments"]:
        try:
            report = export_existing(
                db_path=db_path, assessment_id=assessment["assessment_id"],
                output_dir=output_dir, format=report_format,
            )
        except Exception as exc:
            raise ReportExportError(exc, completed) from exc
        completed.append({
            "bid_no": assessment["bid_no"],
            "assessment_id": assessment["assessment_id"],
            "files": report["files"],
        })
    return completed


def _number(text: str, name: str) -> int | None:
    value = text.strip()
    if not value:
        return None
    if not value.isascii() or not value.isdecimal():
        raise ValueError(f"{name} must be a nonnegative integer or blank")
    return int(value)


def _profile_from_fields(fields: dict[str, str]) -> CompanyProfile:
    def comma_list(raw: str) -> tuple[str, ...] | None:
        value = raw.strip()
        return tuple(piece.strip() for piece in value.split(",") if piece.strip()) if value else None

    return CompanyProfile(
        profile_id=fields["profile_id"].strip(),
        region=fields["region"].strip() or None,
        categories=comma_list(fields["categories"]),
        licenses=comma_list(fields["licenses"]),
        staff_count=_number(fields["staff_count"], "staff_count"),
        experience_total_krw=_number(fields["experience_total_krw"], "experience"),
    )


def run_gui() -> int:
    """Tkinter local desktop form. UI prompts confirmation before any DB write."""
    import tkinter as tk
    from tkinter import filedialog, messagebox

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError("Graphical desktop unavailable; use CLI --csv --profile --source-id") from exc
    root.title("BID OWL — 로컬 CSV 가져오기")
    root.minsize(575, 540)
    fields = {}
    labels = [
        ("csv", "입찰공고 CSV 파일"),
        ("source_id", "자료 출처 ID"),
        ("profile_id", "회사 프로필 ID"),
        ("region", "사업장 소재지"),
        ("categories", "업종 (쉼표 구분)"),
        ("licenses", "면허 (쉼표 구분)"),
        ("staff_count", "보유 인력 수 (미확인 시 공란)"),
        ("experience_total_krw", "실적 합계 원 (미확인 시 공란)"),
    ]
    tk.Label(root, text="회사 정보 및 공고 CSV 등록 — 실제 데이터는 이 PC에만 보관됩니다.",
             anchor="w", wraplength=535).grid(row=0, column=0, columnspan=3, padx=12, pady=12, sticky="w")
    for index, (key, label) in enumerate(labels, 1):
        tk.Label(root, text=label, anchor="w").grid(row=index, column=0, padx=12, pady=5, sticky="w")
        variable = tk.StringVar(root)
        fields[key] = variable
        tk.Entry(root, textvariable=variable, width=39).grid(
            row=index, column=1, padx=5, pady=5, sticky="ew"
        )
        if key == "csv":
            def browse():
                chosen = filedialog.askopenfilename(
                    parent=root, title="CSV 선택",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                )
                if chosen:
                    fields["csv"].set(chosen)
                    if not fields["source_id"].get():
                        fields["source_id"].set("LOCAL-" + Path(chosen).stem[:70])
            tk.Button(root, text="찾기", command=browse).grid(row=index, column=2, padx=8)
    root.grid_columnconfigure(1, weight=1)

    def load_company_json():
        chosen = filedialog.askopenfilename(
            parent=root, title="기존 회사 JSON 불러오기",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not chosen:
            return
        try:
            company = load_profile_file(chosen)
            fields["profile_id"].set(company.profile_id)
            fields["region"].set(company.region or "")
            fields["categories"].set(",".join(company.categories) if company.categories is not None else "")
            fields["licenses"].set(",".join(company.licenses) if company.licenses is not None else "")
            fields["staff_count"].set(str(company.staff_count) if company.staff_count is not None else "")
            fields["experience_total_krw"].set(
                str(company.experience_total_krw) if company.experience_total_krw is not None else ""
            )
        except (OSError, ValueError) as exc:
            messagebox.showerror("파일 오류", str(exc), parent=root)

    tk.Button(root, text="기존 회사 JSON 불러오기 (선택)", command=load_company_json).grid(
        row=9, column=0, columnspan=3, pady=9
    )
    force_var = tk.BooleanVar(root, value=False)
    tk.Checkbutton(
        root,
        text="저장된 판정도 모두 재평가 (규칙 엔진 업데이트 후 권장)",
        variable=force_var,
    ).grid(row=12, column=0, columnspan=3, padx=12, sticky="w")
    create_reports = tk.BooleanVar(root, value=True)
    report_format = tk.StringVar(root, value="xlsx")
    tk.Checkbutton(
        root, text="가져오기 성공 후 Excel/PDF 보고서 생성 (출력 폴더 선택)",
        variable=create_reports,
    ).grid(row=13, column=0, columnspan=3, padx=12, sticky="w")
    tk.Label(root, text="보고서 형식").grid(row=14, column=0, padx=12, sticky="w")
    tk.OptionMenu(root, report_format, "xlsx", "pdf", "both").grid(
        row=14, column=1, sticky="w"
    )
    confirmed = {"db": None, "status": "CANCELLED"}

    def submit():
        try:
            company = _profile_from_fields({k: fields[k].get() for k in fields if k != "csv" and k != "source_id"})
            plan = prepare_import(
                csv_path=fields["csv"].get(), source_id=fields["source_id"].get(),
                profile=company,
            )
            summary = plan_summary(plan)
            report_folder = None
            if create_reports.get():
                chosen = filedialog.askdirectory(
                    parent=root, title="저장 후 보고서를 만들 폴더 선택"
                )
                if not chosen:
                    return  # Cancel before *any* database mutation.
                report_folder = Path(chosen).expanduser().resolve()
                if not report_folder.is_dir():
                    raise ValueError("Report output must be an existing directory")
                if report_format.get() in ("pdf", "both"):
                    check_pdf_support()  # Validate optional PDF dependency before write.
            confirmation = (
                f"공고 {summary['bid_count']:,}건\n회사: {summary['company_id']}\n"
                f"출처: {summary['source_id']}\nDB: {summary['database']}\n"
                f"기존 DB 백업: {'필수·자동 생성' if summary['backup_required'] else '신규 DB라 불필요'}\n\n"
                + (f"보고서: {report_format.get()} → {report_folder}\n\n"
                   if report_folder is not None else "보고서 생성: 하지 않음\n\n")
                + "지금 가져오기를 실행하시겠습니까?"
            )
            if not messagebox.askyesno("검증 완료 — 적용 확인", confirmation, parent=root):
                return
            result = apply_import(plan, force_reassess=force_var.get())
            counts = result["eligibility_counts"]
            confirmed["status"] = "IMPORTED"
            confirmed["db"] = plan.db_path
            completed_reports = []
            report_error = None
            if report_folder is not None:
                try:
                    completed_reports = export_saved_assessments(
                        result, db_path=plan.db_path,
                        output_dir=report_folder, report_format=report_format.get(),
                    )
                except ReportExportError as exc:
                    report_error = exc
                    completed_reports = list(exc.completed)
                    confirmed["status"] = "IMPORTED_EXPORT_FAILED"
            if report_error is not None:
                messagebox.showwarning(
                    "공고 DB 저장 성공 · 보고서 일부 실패",
                    f"공고와 판정은 이미 저장됐습니다. 다시 등록하지 마세요.\n"
                    f"DB: {plan.db_path}\n백업: {result['backup'] or '없음'}\n"
                    f"완료 보고서: {len(completed_reports)}건\n"
                    f"보고서 오류: {type(report_error.cause).__name__}: {report_error}\n"
                    "기존 파일을 덮어쓰지 말고 새 폴더에 저장된 판정만 재출력하세요.",
                    parent=root,
                )
            show = (
                f"새 판정 {result['assessments_saved']:,}건 · 기존 판정 재사용 {result['assessments_reused']:,}건\n"
                f"PASS {counts['PASS']} / FAIL {counts['FAIL']} / UNKNOWN {counts['UNKNOWN']}\n"
                f"백업: {result['backup'] or '기존 DB 없음'}\n"
                f"생성된 보고서: {len(completed_reports)}건"
                + (f" · 폴더: {report_folder}" if report_folder is not None else "")
                + "\n\n공고 화면을 바로 열겠습니까? (이 창 이후 종료는 콘솔 Ctrl+C)"
            )
            confirmed["open"] = messagebox.askyesno("로컬 가져오기 완료", show, parent=root)
            root.destroy()
        except (OSError, ValueError, TypeError, CSVImportError, sqlite3.Error, RuntimeError) as exc:
            messagebox.showerror("검증 또는 저장 실패", str(exc)[:1000], parent=root)

    tk.Button(root, text="검증 후 백업·가져오기", command=submit).grid(
        row=10, column=0, columnspan=3, pady=14
    )
    tk.Label(root, text="빈칸은 미확인(UNKNOWN)입니다. 데모 데이터·실제 회사 정보를 혼합하지 마세요.",
             wraplength=545).grid(row=11, column=0, columnspan=3, pady=5)
    root.mainloop()
    if confirmed.get("open") and confirmed["db"] is not None:
        with make_server(confirmed["db"], 0) as server:
            url = f"http://127.0.0.1:{server.server_port}/"
            print(f"BID OWL LOCAL VIEWER: {url} — 종료 Ctrl+C", flush=True)
            webbrowser.open(url, new=2)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    return 0 if confirmed["status"] in ("IMPORTED", "CANCELLED") else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL offline company + CSV onboarding")
    parser.add_argument("--csv", help="User-selected tender CSV (required for CLI)")
    parser.add_argument("--profile", help="User-selected company profile JSON (required for CLI)")
    parser.add_argument("--source-id", help="Stable source ID, required for CLI")
    parser.add_argument("--db", help="Local BID OWL SQLite destination (default OS-local app data)")
    parser.add_argument("--apply", action="store_true", help="Commit after preflight and backup; CLI preview by default")
    parser.add_argument("--force-reassess", action="store_true", help="Regenerate all assessments after rules-engine upgrades")
    parser.add_argument("--export-dir", help="After --apply, export reports for exactly the imported assessment IDs")
    parser.add_argument("--report-format", choices=("xlsx", "pdf", "both"), default="xlsx",
                        help="Local report output format when --export-dir is used (default xlsx)")
    args = parser.parse_args(argv)
    if not any((args.csv, args.profile, args.source_id, args.db, args.apply, args.force_reassess, args.export_dir)):
        try:
            return run_gui()
        except (ImportError, OSError, RuntimeError) as exc:
            print(f"LOCAL_GUI_UNAVAILABLE: {exc}", file=sys.stderr)
            return 2
    if not all((args.csv, args.profile, args.source_id)):
        parser.error("CLI requires --csv --profile --source-id")
    try:
        if args.export_dir and not args.apply:
            raise ValueError("--export-dir requires explicit --apply")
        if args.export_dir:
            export_dir = Path(args.export_dir).expanduser().resolve()
            if export_dir.exists() and not export_dir.is_dir():
                raise ValueError("Report output path exists but is not a directory")
            if args.report_format in ("pdf", "both"):
                check_pdf_support()  # fail before modifying any customer DB
        plan = prepare_import(
            csv_path=args.csv, profile=load_profile_file(args.profile),
            source_id=args.source_id, db_path=args.db,
        )
        outcome = apply_import(plan, force_reassess=args.force_reassess) if args.apply else plan_summary(plan)
        if args.export_dir:
            # Registration is ALREADY committed; a later report error cannot
            # truthfully be called an import failure or silently rolled back.
            try:
                completed_reports = export_saved_assessments(
                    outcome, db_path=plan.db_path, output_dir=export_dir,
                    report_format=args.report_format,
                )
            except ReportExportError as exc:
                outcome.update({
                    "status": "IMPORTED_EXPORT_FAILED",
                    "reports": list(exc.completed),
                    "export_error_type": type(exc.cause).__name__,
                    "export_error": str(exc),
                    "notice": "Database import succeeded. Report export failed; saved "
                              "assessments and backups remain unchanged. Inspect "
                              "completed reports before attempting retry.",
                })
                print(json.dumps(outcome, ensure_ascii=False, indent=2), file=sys.stderr)
                return 2
            outcome["reports"] = completed_reports
            outcome["status"] = "IMPORTED_AND_EXPORTED"
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
        return 0
    except CSVImportError as exc:
        print(json.dumps({
            "status": "INPUT_REJECTED",
            "issues": [{"line": issue.line, "field": issue.field,
                        "code": issue.code, "message": issue.message} for issue in exc.issues]
        }, ensure_ascii=False), file=sys.stderr)
    except (OSError, ValueError, TypeError, sqlite3.Error, RuntimeError) as exc:
        print(json.dumps({"status": "IMPORT_FAILED", "reason": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

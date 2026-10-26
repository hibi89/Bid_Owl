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
from bidowl.schema import MAX_CSV_BYTES
from bidowl.store import default_database_path
from profile_workflow import load_profile_file
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
    present, version, action = _existing_db_state(destination, profile)
    return ImportPlan(
        db_path=destination, source_id=source_id, csv_path=source,
        csv_sha256=hashlib.sha256(csv_bytes).hexdigest(), bids=tuple(bids),
        profile=profile, existing_db=present,
        existing_profile_version=version, profile_action=action,
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
) -> str | None:
    """Reuse only a snapshot matching both revisions and today's expiry.

    A bid can pass its deadline without a data revision. An assessment from
    before that boundary must be regenerated, not silently reused.
    """
    row = store.db.execute("""
        SELECT b.latest_version,
               p.latest_version AS current_profile_version,
               a.bid_version, a.profile_version, a.status, a.is_expired
        FROM bids b
        JOIN profiles p ON p.profile_id = ?
        LEFT JOIN assessments a ON a.id = (
            SELECT x.id FROM assessments x
            WHERE x.source_id = b.source_id AND x.bid_no = b.bid_no
              AND x.profile_id = ?
            ORDER BY x.id DESC LIMIT 1
        )
        WHERE b.source_id = ? AND b.bid_no = ?
    """, (profile_id, profile_id, source_id, bid_no)).fetchone()
    if row is not None and row["current_profile_version"] != profile_version:
        raise ValueError("Company profile changed while importing; retry")
    if (row is not None and row["status"] in ("PASS", "FAIL", "UNKNOWN")
            and row["bid_version"] == row["latest_version"]
            and row["profile_version"] == profile_version
            and bool(row["is_expired"]) == is_expired):
        return str(row["status"])
    return None


def apply_import(plan: ImportPlan) -> dict:
    """Explicitly called only after review/consent. Fail closed on changed DB.

    A backup protects an existing DB before the first persistent mutation.
    Multi-stage import/profile/assess writes are NOT a single transaction:
    on any post-backup failure, report possible partial writes and keep backup.
    """
    if not isinstance(plan, ImportPlan):
        raise TypeError("Expected an ImportPlan from prepare_import")
    # Input file may be changed after preview; require identical bytes.
    if plan.csv_path.stat().st_size > MAX_CSV_BYTES:
        raise ValueError("CSV grew beyond 10 MiB since preview")
    actual = plan.csv_path.read_bytes()
    if len(actual) > MAX_CSV_BYTES:
        raise ValueError("CSV grew beyond 10 MiB since preview")
    if hashlib.sha256(actual).hexdigest() != plan.csv_sha256:
        raise ValueError("CSV changed after preview; review it again before importing")
    if plan.db_path.exists() != plan.existing_db:
        raise ValueError("Database creation/deletion detected since preview; retry")
    # A second read-only preflight catches changed profile/version/schema.
    current_db, version, action = _existing_db_state(plan.db_path, plan.profile)
    if (current_db, version, action) != (
        plan.existing_db, plan.existing_profile_version, plan.profile_action
    ):
        raise ValueError("Database/profile changed since preview; retry")
    backup = None
    started_writing = False
    # sqlite3.connect() creates absent files without exclusivity.
    # Reserve a truly new DB with O_EXCL ("xb") so a file appearing
    # between read-only preflight and open cannot be silently adopted.
    if not plan.existing_db:
        plan.db_path.parent.mkdir(parents=True, exist_ok=True)
        with plan.db_path.open("xb"):
            pass
    try:
        with BidOwlStore(plan.db_path) as store:
            if plan.existing_db:
                backup = store.backup_to(_new_backup_path(plan.db_path))
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
            for bid in plan.bids:
                checked_at = datetime.now(timezone.utc)
                previous_status = _reusable_assessment_status(
                    store, source_id=plan.source_id, bid_no=bid.bid_no,
                    profile_id=plan.profile.profile_id,
                    profile_version=profile_version,
                    is_expired=bid.is_expired(checked_at),
                )
                if previous_status is not None:
                    reused_assessments += 1
                    counts[previous_status] += 1
                    continue
                _, outcome = store.assess_and_record(
                    plan.source_id, bid.bid_no, plan.profile.profile_id,
                    expected_profile_version=profile_version,
                    checked_at=checked_at,
                )
                saved_assessments += 1
                counts[outcome.status] += 1
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
        "eligibility_counts": counts,
        "notice": "Rule screening only; check the original tender before any bid.",
    }


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
    root.minsize(575, 480)
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
    confirmed = {"db": None, "status": "CANCELLED"}

    def submit():
        try:
            company = _profile_from_fields({k: fields[k].get() for k in fields if k != "csv" and k != "source_id"})
            plan = prepare_import(
                csv_path=fields["csv"].get(), source_id=fields["source_id"].get(),
                profile=company,
            )
            summary = plan_summary(plan)
            confirmation = (
                f"공고 {summary['bid_count']:,}건\n회사: {summary['company_id']}\n"
                f"출처: {summary['source_id']}\nDB: {summary['database']}\n"
                f"기존 DB 백업: {'필수·자동 생성' if summary['backup_required'] else '신규 DB라 불필요'}\n\n"
                "지금 가져오기를 실행하시겠습니까?"
            )
            if not messagebox.askyesno("검증 완료 — 적용 확인", confirmation, parent=root):
                return
            result = apply_import(plan)
            counts = result["eligibility_counts"]
            confirmed["status"] = "IMPORTED"
            confirmed["db"] = plan.db_path
            show = (
                f"새 판정 {result['assessments_saved']:,}건 · 기존 판정 재사용 {result['assessments_reused']:,}건\n"
                f"PASS {counts['PASS']} / FAIL {counts['FAIL']} / UNKNOWN {counts['UNKNOWN']}\n"
                f"백업: {result['backup'] or '기존 DB 없음'}\n\n"
                "공고 화면을 바로 열겠습니까? (이 창 이후 종료는 콘솔 Ctrl+C)"
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
    args = parser.parse_args(argv)
    if not any((args.csv, args.profile, args.source_id, args.db, args.apply)):
        try:
            return run_gui()
        except (ImportError, OSError, RuntimeError) as exc:
            print(f"LOCAL_GUI_UNAVAILABLE: {exc}", file=sys.stderr)
            return 2
    if not all((args.csv, args.profile, args.source_id)):
        parser.error("CLI requires --csv --profile --source-id")
    try:
        plan = prepare_import(
            csv_path=args.csv, profile=load_profile_file(args.profile),
            source_id=args.source_id, db_path=args.db,
        )
        outcome = apply_import(plan) if args.apply else plan_summary(plan)
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

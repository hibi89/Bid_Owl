"""BID OWL P2-03 explicit local profile revision and optional re-assessment.

This is deliberately a CLI, NOT a browser mutation endpoint. User profiles remain
in a local SQLite file; no third-party transmission or background updates.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path

from bidowl import BidOwlStore, CompanyProfile
from bidowl.store import default_database_path

MAX_PROFILE_BYTES = 65536
MAX_REASSESS = 10000


class ReadOnlyProfileStore:
    """Preflight a real schema-v1 database without opening any writable connection."""

    def __init__(self, path: Path):
        self.db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
        self.db.row_factory = sqlite3.Row
        try:
            self.db.execute("PRAGMA query_only=ON")
            if self.db.execute("PRAGMA user_version").fetchone()[0] != 1:
                raise ValueError("Not a BID OWL schema-v1 database")
            needed = {"profiles", "profile_versions", "bids"}
            found = {r[0] for r in self.db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            if not needed <= found:
                raise ValueError("Missing BID OWL data tables")
        except BaseException:
            self.db.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.db.close()

    def get_profile(self, profile_id: str) -> CompanyProfile | None:
        row = self.db.execute("""SELECT v.payload FROM profiles p
            JOIN profile_versions v ON p.profile_id=v.profile_id AND p.latest_version=v.version
            WHERE p.profile_id=?""", (profile_id,)).fetchone()
        return CompanyProfile.from_mapping(json.loads(row["payload"])) if row else None


def load_profile_file(path: str | Path) -> CompanyProfile:
    """Validate complete JSON before opening any writable database."""
    source = Path(path).expanduser().resolve()
    if source.stat().st_size > MAX_PROFILE_BYTES:
        raise ValueError("Profile JSON exceeds 64 KiB")
    try:
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid UTF-8 profile JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("Company profile must be a JSON object")
    profile = CompanyProfile.from_mapping(payload)
    if len(profile.profile_id) > 300 or any(
        isinstance(value, str) and len(value) > 300 for value in (profile.region,)
    ):
        raise ValueError("Profile identifier and region must not exceed 300 characters")
    for values in (profile.categories, profile.licenses):
        if values is not None and (len(values) > 100 or any(len(value) > 300 for value in values)):
            raise ValueError("Profile lists are limited to 100 entries of 300 characters")
    return profile


def execute(
    *,
    db_path: str | Path,
    profile_path: str | Path,
    expected_version: int = 0,
    create: bool = False,
    reassess: bool = False,
    apply: bool = False,
    backup_path: str | Path | None = None,
    max_reassess: int = MAX_REASSESS,
) -> dict:
    """Preview by default; only --apply can mutate local DB after backup."""
    profile = load_profile_file(profile_path)
    db = Path(db_path).expanduser().resolve()
    if not db.is_file():
        raise FileNotFoundError("Existing BID OWL SQLite database required")
    if type(expected_version) is not int or expected_version < 0:
        raise ValueError("expected_version must be nonnegative integer")
    if type(max_reassess) is not int or not 1 <= max_reassess <= MAX_REASSESS:
        raise ValueError("max_reassess must be 1..10000")
    if create and expected_version:
        raise ValueError("Create cannot specify a previous version")
    if apply and backup_path is None:
        raise ValueError("--backup is mandatory for --apply")
    if apply and Path(backup_path).expanduser().resolve() == db:
        raise ValueError("Backup must differ from the active database")

    # Preview itself opens exactly one mode=ro connection. Apply preflights
    # schema read-only before it acquires a separate write-capable store.
    if apply:
        with ReadOnlyProfileStore(db):
            pass
    with (BidOwlStore(db) if apply else ReadOnlyProfileStore(db)) as store:
        existing_row = store.db.execute(
            "SELECT latest_version FROM profiles WHERE profile_id=?", (profile.profile_id,)
        ).fetchone()
        version = int(existing_row["latest_version"]) if existing_row else 0
        if create and existing_row:
            raise ValueError("Profile already exists; use edit mode")
        if not create and not existing_row:
            raise ValueError("Profile not found; use --create to make a new profile")
        if not create and expected_version != version:
            raise ValueError("Profile version mismatch; refresh the profile before editing")
        old = store.get_profile(profile.profile_id) if existing_row else None
        changed = old is None or asdict(old) != asdict(profile)
        bid_keys = (
            [(r["source_id"], r["bid_no"]) for r in store.db.execute(
                "SELECT source_id,bid_no FROM bids ORDER BY source_id,bid_no"
            )] if reassess else []
        )
        if len(bid_keys) > max_reassess:
            raise ValueError("Too many bids for one re-assessment; increase --max-reassess deliberately")

        summary = {
            "status": "PREVIEW",
            "profile_id": profile.profile_id,
            "previous_version": version,
            "planned_version": version + int(changed),
            "changed": changed,
            "reassess_count": len(bid_keys),
            "backup": None,
            "assessments_saved": 0,
            "notice": "This is rule screening only; a human must check source procurement documents.",
        }
        if not apply or (not changed and not bid_keys):
            summary["status"] = "PREVIEW" if not apply else "UNCHANGED"
            return summary

        # Physical, consistent, non-overwriting backup BEFORE first persistent change.
        destination = Path(backup_path).expanduser().resolve()
        saved_backup = store.backup_to(destination)
        summary["backup"] = str(saved_backup)
        saved = 0
        profile_committed = False
        try:
            # Legacy schema-v1 databases have no policy provenance table.
            # This additive change is allowed ONLY after backup_to succeeds.
            # The old assessments stay unproven; reassessed rows record their
            # real engine hash inside BidOwlStore.assess_and_record.
            store.db.execute("""
                CREATE TABLE IF NOT EXISTS assessment_engine_provenance (
                    assessment_id INTEGER PRIMARY KEY,
                    engine_hash TEXT NOT NULL CHECK(length(engine_hash) = 64),
                    FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
                )
            """)
            if changed:
                summary["planned_version"] = store.save_profile(profile, expected_version=version)
                profile_committed = True
            for source_id, bid_no in bid_keys:
                store.assess_and_record(source_id, bid_no, profile.profile_id,
                    expected_profile_version=summary["planned_version"])
                saved += 1
        except BaseException as exc:
            # No other process may silently overwrite a newer profile version.
            # Earlier per-bid commits can still exist if a later assessment fails.
            if (isinstance(exc, ValueError) and "Profile version mismatch" in str(exc)
                    and saved == 0 and not profile_committed):
                raise ValueError(
                    f"CONFLICT_NO_WRITE: {exc}; backup retained at {saved_backup}"
                ) from exc
            raise RuntimeError(
                f"PARTIAL_WRITE: {saved}/{len(bid_keys)} assessments committed; "
                f"backup retained at {saved_backup}. Inspect DB before manual restore."
            ) from exc
        summary["status"] = "APPLIED"
        summary["assessments_saved"] = saved
        return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL offline company profile plan/apply")
    parser.add_argument("--db", default=str(default_database_path()), help="Existing local BID OWL DB")
    parser.add_argument("--profile-file", required=True, help="Validated JSON profile file")
    parser.add_argument("--expected-version", type=int, default=0, help="Current profile version for edit")
    parser.add_argument("--create", action="store_true", help="Create new profile, not edit existing")
    parser.add_argument("--reassess", action="store_true", help="Reassess all local bids after edit")
    parser.add_argument("--max-reassess", type=int, default=MAX_REASSESS)
    parser.add_argument("--backup", help="New, previously nonexistent backup DB file")
    parser.add_argument("--apply", action="store_true", help="Explicitly commit after automatic backup")
    args = parser.parse_args(argv)
    try:
        outcome = execute(db_path=args.db, profile_path=args.profile_file,
            expected_version=args.expected_version, create=args.create,
            reassess=args.reassess, apply=args.apply, backup_path=args.backup,
            max_reassess=args.max_reassess)
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, sqlite3.Error, RuntimeError) as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

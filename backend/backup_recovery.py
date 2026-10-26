"""Offline BID OWL v1 backup inspection and non-destructive recovery.

Preview NEVER creates files. --apply restores into a *new* destination only;
it cannot replace the live database, delete the source backup, or activate it.
All SQLite checks and copying are local. No network, AI, or PDF dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from bidowl.store import SCHEMA_VERSION, database_file_identity

REQUIRED_TABLES = (
    "profiles", "profile_versions", "bids", "bid_versions", "import_runs",
    "assessments", "rule_assessments",
)
REPORT_COUNTS = ("profiles", "bids", "assessments", "import_runs")
# Deterministic evidence coverage includes every version and immutable rule
# snapshot. Only hard-coded table names are ever interpolated into SQL.
EVIDENCE_TABLES = (
    "profiles", "profile_versions", "bids", "bid_versions",
    "import_runs", "assessments", "rule_assessments",
)
EVIDENCE_NAMESPACE = b"BIDOWL-RECOVERY-EVIDENCE-v1\0"
CHUNK_BYTES = 1024 * 1024


@dataclass(frozen=True)
class RecoveryPlan:
    source: Path
    destination: Path
    source_identity: tuple[int, int, int, int]
    source_sha256: str
    counts: tuple[tuple[str, int], ...]
    policy_provenance: bool
    evidence_sha256: str


def _source_connection(path: Path) -> sqlite3.Connection:
    # mode=ro never silently creates an absent backup file.
    connection = sqlite3.connect(
        path.resolve().as_uri() + "?mode=ro", uri=True, timeout=10,
    )
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only=ON")
    except BaseException:
        connection.close()
        raise
    return connection


def _validate_v1(connection: sqlite3.Connection) -> tuple[tuple[tuple[str, int], ...], bool]:
    """Check the *whole* SQLite database before it can be called recoverable."""
    if connection.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
        raise ValueError("Not a supported BID OWL SQLite schema-v1 backup")
    tables = {r[0] for r in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    if not set(REQUIRED_TABLES).issubset(tables):
        raise ValueError("Missing BID OWL tables; refuse incomplete backup")
    integrity = [r[0] for r in connection.execute("PRAGMA integrity_check")]
    if integrity != ["ok"]:
        raise ValueError("SQLite integrity_check failed; refuse corrupt backup")
    if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise ValueError("SQLite foreign key integrity failed")
    counts = tuple(
        (name, int(connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]))
        for name in REPORT_COUNTS  # constant, NEVER interpolated user input
    )
    return counts, "assessment_engine_provenance" in tables


def _evidence_hash(connection: sqlite3.Connection, *, has_policy: bool) -> str:
    """Stream a digest of every version, assessment, rule and policy row.

    Counts alone cannot detect same-count value changes. rowid provides a
    stable ordering for the supported BID OWL v1 tables. Serialize each cell
    with explicit type tags to avoid text/int/NULL/BLOB ambiguity.
    """
    digest = hashlib.sha256(EVIDENCE_NAMESPACE)
    table_names = EVIDENCE_TABLES + (
        ("assessment_engine_provenance",) if has_policy else ()
    )
    for table in table_names:
        digest.update(table.encode("ascii") + b"\0")
        cursor = connection.execute(f'SELECT * FROM "{table}" ORDER BY rowid')
        for row in cursor:
            cells = []
            for value in row:
                if value is None:
                    cells.append(("null", None))
                elif isinstance(value, bytes):
                    cells.append(("blob", value.hex()))
                elif isinstance(value, int):
                    cells.append(("int", value))
                elif isinstance(value, float):
                    cells.append(("float", value.hex()))
                else:
                    cells.append(("text", value))
            serialized = json.dumps(
                cells, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
            ).encode("utf-8")
            digest.update(len(serialized).to_bytes(8, "big"))
            digest.update(serialized)
        digest.update(b"\xff")
    return digest.hexdigest()


def _file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_BYTES):
            sha.update(chunk)
    return sha.hexdigest()


def _source_snapshot(path: Path) -> tuple[
    tuple[int, int, int, int], str, tuple[tuple[str, int], ...], bool, str,
]:
    if not path.is_file():
        raise FileNotFoundError(f"Backup not found: {path}")
    # An actively journalled raw DB copy may omit committed WAL transactions.
    # Fail closed and ask the user to create a consistent SQLite backup first.
    for suffix in ("-wal", "-journal", "-shm"):
        if Path(str(path) + suffix).exists():
            raise ValueError("Backup has an active WAL/journal sidecar; use a consistent SQLite backup")
    identity = database_file_identity(path)
    with closing(_source_connection(path)) as connection:
        # One read transaction keeps count + evidence fingerprint consistent
        # even if another SQLite connection attempts to update at the time.
        connection.execute("BEGIN")
        counts, has_policy = _validate_v1(connection)
        evidence = _evidence_hash(connection, has_policy=has_policy)
        connection.execute("ROLLBACK")  # release read snapshot; no writes
    checksum = _file_hash(path)
    # Sidecars can appear while an external process starts writing. A
    # standalone recoverable snapshot must remain journal-free throughout.
    for suffix in ("-wal", "-journal", "-shm"):
        if Path(str(path) + suffix).exists():
            raise ValueError("Backup journal sidecar appeared during inspection")
    if database_file_identity(path) != identity:
        raise ValueError("Backup changed while being inspected; retry after stopping writers")
    return identity, checksum, counts, has_policy, evidence


def prepare_recovery(source: str | Path, destination: str | Path) -> RecoveryPlan:
    """Read-only validation and digest; never touches the destination directory."""
    src = Path(source).expanduser().resolve()
    dst = Path(destination).expanduser().resolve()
    if src == dst:
        raise ValueError("Restored output must not be the source backup")
    if dst.exists():
        raise FileExistsError(f"Destination already exists, refusing overwrite: {dst}")
    identity, checksum, counts, policy, evidence = _source_snapshot(src)
    return RecoveryPlan(src, dst, identity, checksum, counts, policy, evidence)


def preview_summary(plan: RecoveryPlan) -> dict:
    if not isinstance(plan, RecoveryPlan):
        raise TypeError("RecoveryPlan required")
    return {
        "status": "RECOVERY_PREVIEW_NO_WRITE",
        "source": str(plan.source),
        "new_destination": str(plan.destination),
        "source_sha256": plan.source_sha256,
        "evidence_sha256": plan.evidence_sha256,
        "schema_version": SCHEMA_VERSION,
        "record_counts": dict(plan.counts),
        "engine_provenance_table": plan.policy_provenance,
        "existing_files_overwritten": False,
        "warning": "Only a NEW offline file is supported. Stop BID OWL before manually switching databases.",
    }


def restore_to_new_file(plan: RecoveryPlan) -> dict:
    """Deliberate restore into a fresh file, with source pinning and verification.

    Never overwrites or automatically swaps an active customer database. On
    error, only a file this invocation exclusively reserved may be deleted.
    """
    if not isinstance(plan, RecoveryPlan):
        raise TypeError("RecoveryPlan required")
    if plan.source == plan.destination:
        raise ValueError("Source and destination must differ")
    rechecked = prepare_recovery(plan.source, plan.destination)
    if (rechecked.source_identity != plan.source_identity
            or rechecked.source_sha256 != plan.source_sha256
            or rechecked.counts != plan.counts
            or rechecked.policy_provenance != plan.policy_provenance
            or rechecked.evidence_sha256 != plan.evidence_sha256):
        raise ValueError("Backup changed since preview; do not restore without reinspection")

    destination = plan.destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    reserved_identity = None
    try:
        # O_EXCL: no overwrite, even if another process created the path
        # between preview and the restore. SQLite mode=rw likewise cannot
        # recreate the file if it disappears after exclusive reservation.
        with destination.open("xb"):
            pass
        reserved_identity = database_file_identity(destination)
        with closing(_source_connection(plan.source)) as src:
            observed_counts, _ = _validate_v1(src)
            if observed_counts != plan.counts:
                raise ValueError("Backup contents changed during restore")
            if database_file_identity(plan.source) != plan.source_identity:
                raise ValueError("Backup file identity changed during restore")
            with closing(sqlite3.connect(
                destination.resolve().as_uri() + "?mode=rw",
                uri=True, timeout=10,
            )) as target:
                if database_file_identity(destination) != reserved_identity:
                    raise ValueError("Destination replaced during restore")
                src.backup(target, pages=256, sleep=0.05)
        if (database_file_identity(plan.source) != plan.source_identity
                or _file_hash(plan.source) != plan.source_sha256):
            raise ValueError("Backup changed during copy; recovery not activated")
        verified_identity, _, verified_counts, policy, evidence = _source_snapshot(destination)
        if (verified_counts != plan.counts
                or policy != plan.policy_provenance
                or evidence != plan.evidence_sha256):
            raise ValueError("Restored evidence content differs from backup preview")
        if verified_identity[:2] != reserved_identity[:2]:
            raise ValueError("Destination changed during verification")
    except BaseException:
        # Only delete an output path if we can establish it is the file
        # WE reserved; never unlink another process's replacement file.
        if reserved_identity is not None:
            try:
                current = database_file_identity(destination)
                if current[:2] == reserved_identity[:2] and current[1] != 0:
                    destination.unlink()
            except OSError:
                pass
        raise
    return {
        "status": "RESTORED_TO_NEW_FILE",
        "new_database": str(destination),
        "source_backup": str(plan.source),
        "source_sha256": plan.source_sha256,
        "evidence_sha256": plan.evidence_sha256,
        "record_counts": dict(verified_counts),
        "original_database_modified": False,
        "activation": "NOT_ACTIVATED; close applications and manually select the verified new DB.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline BID OWL v1 backup preview and non-overwriting restore"
    )
    parser.add_argument("--source", required=True, help="Existing BID OWL SQLite backup")
    parser.add_argument("--destination", required=True, help="NEW SQLite output file, never overwrite")
    parser.add_argument("--apply", action="store_true",
                        help="After validation, create and verify new DB (no activation)")
    args = parser.parse_args(argv)
    try:
        plan = prepare_recovery(args.source, args.destination)
        result = restore_to_new_file(plan) if args.apply else preview_summary(plan)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
        print(json.dumps({
            "status": "RECOVERY_FAILED", "type": type(exc).__name__,
            "reason": str(exc),
        }, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

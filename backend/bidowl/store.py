"""BID OWL local SQLite storage: versioned imports and immutable evidence snapshots.

Bids and profiles are never overwritten in history. This module makes no
network calls, contains no law interpreter and accepts no API credentials.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from contextlib import closing, contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

from .engine_identity import engine_fingerprint
from .eligibility import EligibilityDecision, evaluate_bid
from .importer import parse_csv
from .profile import CompanyProfile
from .schema import Bid, Requirement

SCHEMA_VERSION = 1


def default_database_path() -> Path:
    """Return platform-local data location, never a location inside GitHub."""
    if sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if not root:
            raise RuntimeError("Windows local application data directory is unavailable")
        return Path(root) / "BID_OWL" / "bidowl.sqlite3"
    root = os.environ.get("XDG_DATA_HOME")
    return (Path(root) if root else Path.home() / ".local" / "share") / "bidowl" / "bidowl.sqlite3"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _profile_payload(profile: CompanyProfile) -> str:
    return _canonical(asdict(profile))


def _bid_payload(bid: Bid) -> str:
    data = asdict(bid)
    data["bid_deadline"] = bid.bid_deadline.isoformat()
    data["data_as_of"] = bid.data_as_of.isoformat() if bid.data_as_of else None
    data.pop("input_line", None)  # not semantically part of a procurement revision
    return _canonical(data)


def _from_bid(payload: str) -> Bid:
    obj = json.loads(payload)
    obj["bid_deadline"] = datetime.fromisoformat(obj["bid_deadline"])
    obj["data_as_of"] = datetime.fromisoformat(obj["data_as_of"]) if obj["data_as_of"] else None
    obj["requirements"] = tuple(Requirement(**rule) for rule in obj["requirements"])
    return Bid(**obj, input_line=0)  # source line belongs to import audit, not canonical record


def _require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 300:
        raise ValueError(f"{name} must be a nonempty string of at most 300 characters")
    return value


@dataclass(frozen=True)
class ImportResult:
    run_id: int
    source_id: str
    file_sha256: str | None
    inserted: int
    revised: int
    unchanged: int


class SchemaVersionError(RuntimeError):
    pass


class BidOwlStore:
    """Open one process-owned connection; use with a context manager.

    API calls to import/profiles/assess are committed separately and atomically.
    Never use this class concurrently from multiple threads; SQLite serializes writers.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path), isolation_level=None, timeout=15)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        try:
            self._initialize()
        except BaseException:
            self.db.close()
            raise

    def __enter__(self) -> "BidOwlStore":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self.db.close()

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _initialize(self) -> None:
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version != 0 and version != SCHEMA_VERSION:
            raise SchemaVersionError(f"unsupported database schema version {version}")
        if version == SCHEMA_VERSION:
            required = {"profiles", "profile_versions", "bids", "bid_versions", "import_runs", "assessments", "rule_assessments"}
            existing = {r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not required.issubset(existing):
                raise SchemaVersionError("database schema is missing required tables")
            return
        # Pre-existing unversioned DBs may have user tables; never assume it is ours.
        if self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' LIMIT 1").fetchone():
            raise SchemaVersionError("unversioned database is not empty; manual migration required")
        self.db.executescript("""
                BEGIN IMMEDIATE;
                CREATE TABLE profiles (
                    profile_id TEXT PRIMARY KEY, latest_version INTEGER NOT NULL
                );
                CREATE TABLE profile_versions (
                    profile_id TEXT NOT NULL, version INTEGER NOT NULL CHECK(version > 0),
                    digest TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL,
                    PRIMARY KEY(profile_id, version),
                    FOREIGN KEY(profile_id) REFERENCES profiles(profile_id)
                );
                CREATE TABLE bids (
                    source_id TEXT NOT NULL, bid_no TEXT NOT NULL, latest_version INTEGER NOT NULL,
                    PRIMARY KEY(source_id, bid_no)
                );
                CREATE TABLE bid_versions (
                    source_id TEXT NOT NULL, bid_no TEXT NOT NULL,
                    version INTEGER NOT NULL CHECK(version > 0), digest TEXT NOT NULL,
                    payload TEXT NOT NULL, created_at TEXT NOT NULL,
                    PRIMARY KEY(source_id, bid_no, version),
                    FOREIGN KEY(source_id, bid_no) REFERENCES bids(source_id, bid_no)
                );
                CREATE TABLE import_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL,
                    file_sha256 TEXT, executed_at TEXT NOT NULL, input_count INTEGER NOT NULL,
                    inserted INTEGER NOT NULL, revised INTEGER NOT NULL, unchanged INTEGER NOT NULL
                );
                CREATE TABLE assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL, bid_no TEXT NOT NULL, bid_version INTEGER NOT NULL,
                    profile_id TEXT NOT NULL, profile_version INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PASS','FAIL','UNKNOWN')),
                    checked_at TEXT NOT NULL, is_expired INTEGER NOT NULL,
                    data_as_of TEXT, requires_human_review INTEGER NOT NULL,
                    final_approval_required INTEGER NOT NULL,
                    FOREIGN KEY(source_id,bid_no,bid_version)
                      REFERENCES bid_versions(source_id,bid_no,version),
                    FOREIGN KEY(profile_id,profile_version)
                      REFERENCES profile_versions(profile_id,version)
                );
                CREATE TABLE rule_assessments (
                    assessment_id INTEGER NOT NULL, position INTEGER NOT NULL,
                    rule_id TEXT NOT NULL, kind TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PASS','FAIL','UNKNOWN')),
                    reason_code TEXT NOT NULL, explanation TEXT NOT NULL,
                    source_text TEXT, source_locator TEXT, requires_human_review INTEGER NOT NULL,
                    PRIMARY KEY(assessment_id,position),
                    FOREIGN KEY(assessment_id) REFERENCES assessments(id)
                );
                -- Additive provenance for all freshly created databases. Old v1
                -- databases are migrated only by an explicit backed-up writer.
                CREATE TABLE assessment_engine_provenance (
                    assessment_id INTEGER PRIMARY KEY,
                    engine_hash TEXT NOT NULL CHECK(length(engine_hash) = 64),
                    FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
                );
                CREATE INDEX idx_assessments_bid ON assessments(source_id,bid_no,id);
                CREATE INDEX idx_import_runs_source ON import_runs(source_id,id);
                PRAGMA user_version = 1;
                COMMIT;
            """)

    def save_profile(self, profile: CompanyProfile, *, expected_version: int | None = None) -> int:
        if not isinstance(profile, CompanyProfile):
            raise TypeError("profile must be CompanyProfile")
        if expected_version is not None and (type(expected_version) is not int or expected_version < 0):
            raise ValueError("expected_version must be a nonnegative integer or None")
        data = _profile_payload(profile)
        digest = _digest(data)
        with self._transaction():
            old = self.db.execute("SELECT latest_version FROM profiles WHERE profile_id=?", (profile.profile_id,)).fetchone()
            actual_version = int(old["latest_version"]) if old else 0
            if expected_version is not None and actual_version != expected_version:
                raise ValueError("Profile version mismatch during save; refresh and retry")
            if old:
                version = old["latest_version"]
                prev = self.db.execute("SELECT digest FROM profile_versions WHERE profile_id=? AND version=?", (profile.profile_id,version)).fetchone()
                if prev["digest"] == digest:
                    return version
                version += 1
                self.db.execute("UPDATE profiles SET latest_version=? WHERE profile_id=?", (version,profile.profile_id))
            else:
                version = 1
                self.db.execute("INSERT INTO profiles(profile_id,latest_version) VALUES (?,?)", (profile.profile_id,version))
            self.db.execute("INSERT INTO profile_versions VALUES (?,?,?,?,?)", (profile.profile_id,version,digest,data,_now()))
            return version

    def get_profile(self, profile_id: str, version: int | None = None) -> CompanyProfile | None:
        if version is None:
            row = self.db.execute("""SELECT v.payload FROM profile_versions v JOIN profiles p
                ON p.profile_id=v.profile_id AND p.latest_version=v.version WHERE p.profile_id=?""", (profile_id,)).fetchone()
        else:
            row = self.db.execute("SELECT payload FROM profile_versions WHERE profile_id=? AND version=?",(profile_id,version)).fetchone()
        return CompanyProfile.from_mapping(json.loads(row["payload"])) if row else None

    def import_csv(self, data: bytes, *, source_id: str) -> ImportResult:
        parsed = parse_csv(data)
        bids = parsed.require_valid()  # validate before touching persistent state
        return self.import_bids(bids, source_id=source_id, file_sha256=hashlib.sha256(data).hexdigest())

    def import_bids(self, bids: Iterable[Bid], *, source_id: str, file_sha256: str | None = None) -> ImportResult:
        source_id = _require_text(source_id, "source_id")
        records = tuple(bids)
        if file_sha256 is not None and (not isinstance(file_sha256,str) or len(file_sha256)!=64 or any(ch not in '0123456789abcdef' for ch in file_sha256)):
            raise ValueError("file_sha256 must be a lowercase SHA-256 hex digest")
        seen: set[str] = set()
        prepared: list[tuple[Bid,str,str]] = []
        for bid in records:
            if not isinstance(bid, Bid) or not bid.bid_no or not bid.title or not bid.agency or not bid.category or type(bid.budget) is not int or bid.budget <= 0:
                raise ValueError("invalid bid record")
            if bid.bid_no in seen:
                raise ValueError("duplicate bid_no in one batch")
            seen.add(bid.bid_no)
            if bid.bid_deadline.utcoffset() is None or (bid.data_as_of is not None and bid.data_as_of.utcoffset() is None):
                raise ValueError("timestamps must be timezone aware")
            payload = _bid_payload(bid)
            prepared.append((bid,payload,_digest(payload)))
        inserted = revised = unchanged = 0
        with self._transaction():
            for bid,payload,digest in prepared:
                row = self.db.execute("SELECT latest_version FROM bids WHERE source_id=? AND bid_no=?", (source_id,bid.bid_no)).fetchone()
                if row:
                    version = row["latest_version"]
                    old = self.db.execute("SELECT digest FROM bid_versions WHERE source_id=? AND bid_no=? AND version=?", (source_id,bid.bid_no,version)).fetchone()
                    if old["digest"] == digest:
                        unchanged += 1
                        continue
                    version += 1
                    revised += 1
                    self.db.execute("UPDATE bids SET latest_version=? WHERE source_id=? AND bid_no=?",(version,source_id,bid.bid_no))
                else:
                    version = 1
                    inserted += 1
                    self.db.execute("INSERT INTO bids VALUES (?,?,?)",(source_id,bid.bid_no,version))
                self.db.execute("INSERT INTO bid_versions VALUES (?,?,?,?,?,?)",(source_id,bid.bid_no,version,digest,payload,_now()))
            cur = self.db.execute("""INSERT INTO import_runs
                (source_id,file_sha256,executed_at,input_count,inserted,revised,unchanged)
                VALUES (?,?,?,?,?,?,?)""",(source_id,file_sha256,_now(),len(records),inserted,revised,unchanged))
            run_id = cur.lastrowid
        return ImportResult(run_id,source_id,file_sha256,inserted,revised,unchanged)

    def get_bid(self, source_id: str, bid_no: str, version: int | None = None) -> Bid | None:
        if version is None:
            row = self.db.execute("""SELECT v.payload FROM bid_versions v JOIN bids b
                ON b.source_id=v.source_id AND b.bid_no=v.bid_no AND b.latest_version=v.version
                WHERE b.source_id=? AND b.bid_no=?""",(source_id,bid_no)).fetchone()
        else:
            row = self.db.execute("SELECT payload FROM bid_versions WHERE source_id=? AND bid_no=? AND version=?",(source_id,bid_no,version)).fetchone()
        return _from_bid(row["payload"]) if row else None

    def bid_versions(self, source_id: str, bid_no: str) -> tuple[sqlite3.Row, ...]:
        return tuple(self.db.execute("""SELECT version,digest,created_at FROM bid_versions
            WHERE source_id=? AND bid_no=? ORDER BY version""",(source_id,bid_no)).fetchall())

    def import_runs(self, source_id: str) -> tuple[sqlite3.Row, ...]:
        return tuple(self.db.execute("SELECT * FROM import_runs WHERE source_id=? ORDER BY id",(source_id,)).fetchall())

    def assess_and_record(self, source_id: str, bid_no: str, profile_id: str, *,
                          checked_at: datetime | None = None,
                          expected_profile_version: int | None = None) -> tuple[int,EligibilityDecision]:
        # Evaluate + save against the SAME stored revisions under write lock.
        if expected_profile_version is not None and (
            type(expected_profile_version) is not int or expected_profile_version <= 0
        ):
            raise ValueError("expected_profile_version must be a positive integer")
        # Resolve identity before starting a DB transaction: if packaged
        # policy sources cannot be verified, do not write unproven PASS results.
        policy_hash = engine_fingerprint()
        with self._transaction():
            bid_row = self.db.execute("SELECT latest_version FROM bids WHERE source_id=? AND bid_no=?",(source_id,bid_no)).fetchone()
            profile_row = self.db.execute("SELECT latest_version FROM profiles WHERE profile_id=?",(profile_id,)).fetchone()
            if bid_row is None or profile_row is None:
                raise KeyError("bid or profile not found")
            if (expected_profile_version is not None
                    and profile_row["latest_version"] != expected_profile_version):
                raise ValueError("Profile version mismatch during assessment")
            bid = self.get_bid(source_id,bid_no,bid_row["latest_version"])
            profile = self.get_profile(profile_id,profile_row["latest_version"])
            outcome = evaluate_bid(bid,profile,checked_at=checked_at)
            cur = self.db.execute("""INSERT INTO assessments
                (source_id,bid_no,bid_version,profile_id,profile_version,status,checked_at,
                is_expired,data_as_of,requires_human_review,final_approval_required)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(
                    source_id,bid_no,bid_row["latest_version"],profile_id,profile_row["latest_version"],
                    outcome.status,outcome.checked_at.isoformat(),int(outcome.is_expired),
                    outcome.data_as_of.isoformat() if outcome.data_as_of else None,
                    int(outcome.requires_human_review),int(outcome.final_approval_required)))
            assessment_id = cur.lastrowid
            for position,decision in enumerate(outcome.decisions):
                self.db.execute("""INSERT INTO rule_assessments
                    (assessment_id,position,rule_id,kind,status,reason_code,explanation,
                     source_text,source_locator,requires_human_review)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",(
                        assessment_id,position,decision.rule_id,decision.kind,decision.status,
                        decision.reason_code,decision.explanation,decision.source_text,
                        decision.source_locator,int(decision.requires_human_review)))
            if self.db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' "
                "AND name='assessment_engine_provenance'"
            ).fetchone():
                # Same write transaction as parent assessment; no half-proven
                # PASS row if provenance insert fails.
                self.db.execute(
                    "INSERT INTO assessment_engine_provenance(assessment_id,engine_hash) VALUES (?,?)",
                    (assessment_id, policy_hash),
                )
            # Older v1 databases WITHOUT the table remain unproven and
            # display UNKNOWN until the backed-up importer upgrades metadata.
        return assessment_id,outcome

    def assessment(self, assessment_id: int) -> tuple[sqlite3.Row, tuple[sqlite3.Row,...]] | None:
        row = self.db.execute("SELECT * FROM assessments WHERE id=?",(assessment_id,)).fetchone()
        if row is None:
            return None
        rules = tuple(self.db.execute("SELECT * FROM rule_assessments WHERE assessment_id=? ORDER BY position",(assessment_id,)).fetchall())
        return row,rules

    def backup_to(self, destination: str | Path) -> Path:
        """Create a consistent SQLite backup. Refuse overwrite to protect existing copies."""
        dest = Path(destination)
        if dest.resolve() == self.path.resolve():
            raise ValueError("backup cannot overwrite the active database")
        dest.parent.mkdir(parents=True,exist_ok=True)
        # 'x' reserves a new destination; never overwrite a user's backup.
        with dest.open("xb"):
            pass
        try:
            # sqlite3.Connection.__exit__ commits/rolls back but does NOT
            # close the handle. Windows otherwise locks this backup file.
            with closing(sqlite3.connect(str(dest))) as target:
                self.db.backup(target)
                if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise sqlite3.DatabaseError("backup integrity check failed")
        except BaseException:
            dest.unlink(missing_ok=True)
            raise
        return dest

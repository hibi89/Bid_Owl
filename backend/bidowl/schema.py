"""BID OWL v1 CSV data contract. The data here is never a legal qualification verdict."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

REQUIRED_COLUMNS = (
    "bid_no", "title", "agency", "category", "bid_deadline", "budget", "requirements"
)
OPTIONAL_COLUMNS = ("source_ref", "data_as_of")
MAX_CSV_BYTES = 10 * 1024 * 1024
MAX_BIDS = 10_000
MAX_REQUIREMENTS_PER_BID = 100


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    line: int
    field: str
    message: str


@dataclass(frozen=True)
class Requirement:
    id: str
    kind: str
    value: Any
    source_text: str | None
    source_locator: str | None


@dataclass(frozen=True)
class Bid:
    bid_no: str
    title: str
    agency: str
    category: str
    bid_deadline: datetime
    budget: int
    requirements: tuple[Requirement, ...]
    source_ref: str | None
    data_as_of: datetime | None
    input_line: int

    def is_expired(self, now: datetime | None = None) -> bool:
        reference = now if now is not None else datetime.now(timezone.utc)
        if reference.tzinfo is None or reference.utcoffset() is None:
            raise ValueError("now must include a time zone")
        return self.bid_deadline <= reference


@dataclass(frozen=True)
class ImportBatch:
    bids: tuple[Bid, ...]
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues

    def require_valid(self) -> tuple[Bid, ...]:
        if self.issues:
            raise CSVImportError(self.issues)
        return self.bids


class CSVImportError(ValueError):
    def __init__(self, issues: tuple[ValidationIssue, ...] | list[ValidationIssue]):
        self.issues = tuple(issues)
        super().__init__(f"CSV import rejected with {len(self.issues)} validation issue(s)")

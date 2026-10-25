"""Fail-closed, offline CSV reader. No partial accepted dataset is ever committed."""
from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .schema import (
    Bid, CSVImportError, ImportBatch, MAX_BIDS, MAX_CSV_BYTES,
    MAX_REQUIREMENTS_PER_BID, OPTIONAL_COLUMNS, REQUIRED_COLUMNS,
    Requirement, ValidationIssue,
)

_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$")
_INTEGER = re.compile(r"^[0-9]+$")
_KNOWN_KINDS = {"region_any", "category_any", "license_all", "staff_min", "experience_total_min_krw"}
_LIST_KINDS = {"region_any", "category_any", "license_all"}
_NUMERIC_KINDS = {"staff_min", "experience_total_min_krw"}


def _timestamp(value: str) -> datetime:
    if not _TIMESTAMP.fullmatch(value):
        raise ValueError("ISO 8601 timestamp with time zone required (e.g. 2027-11-01T17:00:00+09:00)")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("timestamp has no time zone")
    return parsed


def _requirements(raw: str, line: int, problems: list[ValidationIssue]) -> tuple[Requirement, ...]:
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        problems.append(ValidationIssue("INVALID_JSON", line, "requirements", "requirements must be a JSON array"))
        return ()
    if not isinstance(parsed, list) or len(parsed) > MAX_REQUIREMENTS_PER_BID:
        problems.append(ValidationIssue("INVALID_REQUIREMENTS", line, "requirements", "expected an array of at most 100 rules"))
        return ()
    rules: list[Requirement] = []
    seen: set[str] = set()
    for i, item in enumerate(parsed):
        field = f"requirements[{i}]"
        if not isinstance(item, dict):
            problems.append(ValidationIssue("INVALID_RULE", line, field, "rule must be a JSON object"))
            continue
        rid, kind = item.get("id"), item.get("kind")
        if not isinstance(rid, str) or not rid.strip() or not isinstance(kind, str) or not kind.strip():
            problems.append(ValidationIssue("INVALID_RULE", line, field, "nonempty string id and kind are required"))
            continue
        if rid in seen:
            problems.append(ValidationIssue("DUPLICATE_RULE_ID", line, field, f"duplicate rule id: {rid}"))
            continue
        seen.add(rid)
        value: Any = item.get("value")
        if kind in _LIST_KINDS and (not isinstance(value, list) or not value or any(not isinstance(v, str) or not v.strip() for v in value)):
            problems.append(ValidationIssue("INVALID_RULE_VALUE", line, field, "expected nonempty array of nonempty strings"))
            continue
        if kind in _NUMERIC_KINDS and (type(value) is not int or value < 0):
            problems.append(ValidationIssue("INVALID_RULE_VALUE", line, field, "expected nonnegative integer"))
            continue
        if kind not in _KNOWN_KINDS and "value" not in item:
            # Unknown rule types are imported only when their payload exists; evaluation will return UNKNOWN.
            problems.append(ValidationIssue("INVALID_RULE_VALUE", line, field, "unknown rule requires a value payload"))
            continue
        source = item.get("source")
        if source is not None and not isinstance(source, dict):
            problems.append(ValidationIssue("INVALID_SOURCE", line, field, "source must be an object or null"))
            continue
        source = source or {}
        if any(k in source and source[k] is not None and not isinstance(source[k], str) for k in ("text", "locator")):
            problems.append(ValidationIssue("INVALID_SOURCE", line, field, "source text and locator must be strings"))
            continue
        rules.append(Requirement(
            id=rid, kind=kind, value=value,
            source_text=(source.get("text") or "").strip() or None,
            source_locator=(source.get("locator") or "").strip() or None,
        ))
    return tuple(rules)


def parse_csv(content: bytes) -> ImportBatch:
    """Return all validation issues. Call require_valid() before persisting any rows."""
    issues: list[ValidationIssue] = []
    if len(content) > MAX_CSV_BYTES:
        return ImportBatch((), (ValidationIssue("FILE_TOO_LARGE", 0, "file", "maximum 10 MiB"),))
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return ImportBatch((), (ValidationIssue("INVALID_ENCODING", 0, "file", "UTF-8 or UTF-8-SIG required"),))
    if not decoded.strip():
        return ImportBatch((), (ValidationIssue("EMPTY_FILE", 0, "file", "CSV is empty"),))

    reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
    try:
        header = next(reader)
        if len(header) != len(set(header)):
            issues.append(ValidationIssue("DUPLICATE_COLUMN", 1, "header", "column names must be unique"))
        missing = set(REQUIRED_COLUMNS) - set(header)
        unknown = set(header) - set(REQUIRED_COLUMNS) - set(OPTIONAL_COLUMNS)
        if missing:
            issues.append(ValidationIssue("MISSING_COLUMN", 1, "header", ", ".join(sorted(missing))))
        if unknown:
            issues.append(ValidationIssue("UNKNOWN_COLUMN", 1, "header", ", ".join(sorted(unknown))))
        if issues:
            return ImportBatch((), tuple(issues))
        found: set[str] = set()
        bids: list[Bid] = []
        for row_index, row in enumerate(reader, start=2):
            if row_index - 1 > MAX_BIDS:
                issues.append(ValidationIssue("ROW_LIMIT", reader.line_num, "file", "maximum 10,000 bids"))
                break
            line = reader.line_num
            if len(row) != len(header):
                issues.append(ValidationIssue("COLUMN_COUNT", line, "row", f"expected {len(header)} cells, got {len(row)}"))
                continue
            record = dict(zip(header, row))
            row_issues: list[ValidationIssue] = []
            for col in REQUIRED_COLUMNS:
                if not record[col].strip():
                    row_issues.append(ValidationIssue("REQUIRED_EMPTY", line, col, "required cell is empty"))
            if row_issues:
                issues.extend(row_issues)
                continue
            bid_no = record["bid_no"].strip()
            if bid_no in found:
                row_issues.append(ValidationIssue("DUPLICATE_BID_NO", line, "bid_no", f"repeated bid_no: {bid_no}"))
            found.add(bid_no)
            try:
                deadline = _timestamp(record["bid_deadline"].strip())
            except ValueError as ex:
                row_issues.append(ValidationIssue("INVALID_DEADLINE", line, "bid_deadline", str(ex)))
                deadline = None
            budget_raw = record["budget"].strip()
            if not _INTEGER.fullmatch(budget_raw) or len(budget_raw) > 20 or int(budget_raw) == 0:
                row_issues.append(ValidationIssue("INVALID_BUDGET", line, "budget", "positive integer KRW required"))
                budget = None
            else:
                budget = int(budget_raw)
            requirements = _requirements(record["requirements"], line, row_issues)
            as_of = None
            if record.get("data_as_of", "").strip():
                try:
                    as_of = _timestamp(record["data_as_of"].strip())
                except ValueError as ex:
                    row_issues.append(ValidationIssue("INVALID_DATA_AS_OF", line, "data_as_of", str(ex)))
            issues.extend(row_issues)
            if not row_issues:
                bids.append(Bid(
                    bid_no=bid_no, title=record["title"].strip(), agency=record["agency"].strip(),
                    category=record["category"].strip(), bid_deadline=deadline, budget=budget,
                    requirements=requirements, source_ref=record.get("source_ref", "").strip() or None,
                    data_as_of=as_of, input_line=line,
                ))
    except csv.Error as ex:
        issues.append(ValidationIssue("MALFORMED_CSV", reader.line_num, "file", str(ex)))
    return ImportBatch(tuple(bids) if not issues else (), tuple(issues))


def load_csv(path: str | Path) -> tuple[Bid, ...]:
    """Load a complete valid dataset or raise; consumers must not persist invalid batches."""
    file = Path(path)
    if file.stat().st_size > MAX_CSV_BYTES:
        raise CSVImportError((ValidationIssue("FILE_TOO_LARGE", 0, "file", "maximum 10 MiB"),))
    return parse_csv(file.read_bytes()).require_valid()

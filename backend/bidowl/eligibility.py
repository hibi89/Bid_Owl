"""Conservative auditable screening: not legal advice or bid submission approval."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from .profile import CompanyProfile
from .schema import Bid, Requirement

Status = Literal["PASS", "FAIL", "UNKNOWN"]


@dataclass(frozen=True)
class RuleDecision:
    rule_id: str
    kind: str
    status: Status
    reason_code: str
    explanation: str
    source_text: str | None
    source_locator: str | None
    requires_human_review: bool


@dataclass(frozen=True)
class EligibilityDecision:
    bid_no: str
    profile_id: str
    status: Status
    checked_at: datetime
    is_expired: bool
    data_as_of: datetime | None
    decisions: tuple[RuleDecision, ...]
    requires_human_review: bool
    final_approval_required: bool = True


def _result(rule: Requirement, status: Status, code: str, explanation: str) -> RuleDecision:
    return RuleDecision(
        rule_id=rule.id, kind=rule.kind, status=status, reason_code=code,
        explanation=explanation, source_text=rule.source_text,
        source_locator=rule.source_locator, requires_human_review=(status == "UNKNOWN"),
    )


def _rule_decision(rule: Requirement, profile: CompanyProfile) -> RuleDecision:
    # Both provenance fields are required to trust a deterministic comparison.
    if not isinstance(rule.source_text, str) or not rule.source_text.strip() or not isinstance(rule.source_locator, str) or not rule.source_locator.strip():
        return _result(rule, "UNKNOWN", "SOURCE_MISSING", "원문 문구 또는 위치가 누락되어 검토가 필요합니다.")

    kind, required = rule.kind, rule.value
    arrays = {"region_any", "category_any", "license_all"}
    numbers = {"staff_min", "experience_total_min_krw"}
    if kind not in arrays | numbers:
        return _result(rule, "UNKNOWN", "UNSUPPORTED_RULE", "지원하지 않는 조건 유형이며 법규 해석을 하지 않습니다.")
    if kind in arrays:
        if not isinstance(required, (list, tuple)) or not required or any(not isinstance(v, str) or not v.strip() for v in required):
            return _result(rule, "UNKNOWN", "INVALID_RULE_VALUE", "조건 값이 유효하지 않습니다.")
    elif type(required) is not int or required < 0:
        return _result(rule, "UNKNOWN", "INVALID_RULE_VALUE", "조건 값이 유효하지 않습니다.")

    if kind == "region_any":
        actual = profile.region
        if actual is None:
            return _result(rule, "UNKNOWN", "PROFILE_MISSING", "회사 소재지 정보가 없습니다.")
        matched = actual in required  # no inferred regional synonyms or hierarchy
    elif kind == "category_any":
        actual = profile.categories
        if actual is None:
            return _result(rule, "UNKNOWN", "PROFILE_MISSING", "회사 업종 정보가 없습니다.")
        matched = bool(set(actual).intersection(required))
    elif kind == "license_all":
        actual = profile.licenses
        if actual is None:
            return _result(rule, "UNKNOWN", "PROFILE_MISSING", "회사 면허 정보가 없습니다.")
        matched = set(required).issubset(actual)
    elif kind == "staff_min":
        actual = profile.staff_count
        if actual is None:
            return _result(rule, "UNKNOWN", "PROFILE_MISSING", "회사 인원 정보가 없습니다.")
        matched = actual >= required
    else:
        actual = profile.experience_total_krw
        if actual is None:
            return _result(rule, "UNKNOWN", "PROFILE_MISSING", "실적 금액 정보가 없습니다.")
        matched = actual >= required

    if matched:
        return _result(rule, "PASS", "MATCH", "입력 프로필과 명시 조건이 정확히 일치하거나 기준을 충족합니다.")
    return _result(rule, "FAIL", "MISMATCH", "입력 프로필과 명시 조건이 일치하지 않거나 기준에 미달합니다.")


def evaluate_bid(bid: Bid, profile: CompanyProfile, *, checked_at: datetime | None = None) -> EligibilityDecision:
    now = checked_at if checked_at is not None else datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("checked_at must be timezone-aware")
    decisions = tuple(_rule_decision(rule, profile) for rule in bid.requirements)
    if not decisions or any(r.status == "UNKNOWN" for r in decisions):
        aggregate: Status = "UNKNOWN"
    else:
        aggregate = "PASS"
    if any(r.status == "FAIL" for r in decisions):
        aggregate = "FAIL"  # a demonstrable failure outranks unresolved rules
    return EligibilityDecision(
        bid_no=bid.bid_no, profile_id=profile.profile_id, status=aggregate,
        checked_at=now, is_expired=bid.is_expired(now), data_as_of=bid.data_as_of,
        decisions=decisions, requires_human_review=any(r.requires_human_review for r in decisions) or not decisions,
    )

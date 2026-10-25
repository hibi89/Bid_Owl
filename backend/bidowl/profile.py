"""Validated in-memory company profile. No legal eligibility claims or persistence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any


@dataclass(frozen=True)
class CompanyProfile:
    """None = missing/unknown. Empty tuple = confirmed empty category/license set."""

    profile_id: str
    region: str | None = None
    categories: tuple[str, ...] | None = None
    licenses: tuple[str, ...] | None = None
    staff_count: int | None = None
    experience_total_krw: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise ValueError("profile_id must be a nonempty string")
        self._check_text("region", self.region)
        for field in ("categories", "licenses"):
            value = getattr(self, field)
            if value is None:
                continue
            if not isinstance(value, tuple) or any(not isinstance(s, str) or not s.strip() for s in value):
                raise ValueError(f"{field} must be a tuple of nonempty strings or None")
            if len(set(value)) != len(value):
                raise ValueError(f"{field} contains duplicate values")
        for field in ("staff_count", "experience_total_krw"):
            value = getattr(self, field)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"{field} must be a nonnegative integer or None")

    @staticmethod
    def _check_text(field: str, value: str | None) -> None:
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"{field} must be a nonempty string or None")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CompanyProfile":
        """Strict user-input boundary. Unknown keys/values are not silently assumed."""
        if not isinstance(raw, Mapping):
            raise ValueError("profile must be a mapping")
        allowed = {"profile_id", "region", "categories", "licenses", "staff_count", "experience_total_krw"}
        extra = set(raw) - allowed
        if extra:
            raise ValueError(f"unsupported profile fields: {', '.join(sorted(map(str, extra)))}")
        kw = dict(raw)
        for field in ("categories", "licenses"):
            value = kw.get(field)
            if value is not None:
                if not isinstance(value, (tuple, list)):
                    raise ValueError(f"{field} must be a list of strings or null")
                kw[field] = tuple(value)
        try:
            return cls(**kw)
        except TypeError as exc:
            raise ValueError("invalid company profile fields") from exc

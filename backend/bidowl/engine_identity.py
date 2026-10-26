"""Deterministic identity of BID OWL's auditable eligibility rule engine.

All policy-relevant local source modules are hashed, not just a manually
maintained version label. Any change to rule behavior, profile normalization
or expiry semantics changes this fingerprint. Never hash customer data.

Packaged builds must include these source resources or an independently
verified immutable policy manifest: missing files fail CLOSED, not as PASS.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

POLICY_FILES = ("eligibility.py", "schema.py", "profile.py", "store.py")
POLICY_NAMESPACE = b"BIDOWL-ELIGIBILITY-POLICY-v1\0"


def engine_fingerprint() -> str:
    root = Path(__file__).resolve().parent
    digest = hashlib.sha256(POLICY_NAMESPACE)
    for name in POLICY_FILES:
        data = (root / name).read_bytes()  # fail closed if unavailable
        digest.update(name.encode("ascii"))
        digest.update(b"\0")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()

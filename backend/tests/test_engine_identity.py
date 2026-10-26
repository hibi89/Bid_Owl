"""P2-16 policy identity: test stable hashing, changes, and fail-closed behavior."""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from bidowl.engine_identity import POLICY_FILES, engine_fingerprint


class EngineIdentityTests(unittest.TestCase):
    def test_local_policy_digest_is_stable_and_sha256(self):
        left = engine_fingerprint()
        right = engine_fingerprint()
        self.assertEqual(left, right)
        self.assertEqual(len(left), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in left))
        self.assertIn("eligibility.py", POLICY_FILES)
        self.assertIn("schema.py", POLICY_FILES)
        self.assertIn("profile.py", POLICY_FILES)
        self.assertIn("store.py", POLICY_FILES)

    def test_modifying_a_policy_file_changes_fingerprint(self):
        prior = engine_fingerprint()
        original = Path.read_bytes

        def changed_bytes(path):
            data = original(path)
            if path.name == "eligibility.py":
                return data + b"\n# SIMULATED_POLICY_CHANGE\n"
            return data

        with patch("bidowl.engine_identity.Path.read_bytes", new=changed_bytes):
            updated = engine_fingerprint()
        self.assertNotEqual(prior, updated)

    def test_missing_policy_source_fails_closed(self):
        original = Path.read_bytes

        def unreadable(path):
            if path.name == "schema.py":
                raise FileNotFoundError("unavailable policy source")
            return original(path)

        with patch("bidowl.engine_identity.Path.read_bytes", new=unreadable):
            with self.assertRaisesRegex(FileNotFoundError, "unavailable"):
                engine_fingerprint()


if __name__ == "__main__":
    unittest.main()

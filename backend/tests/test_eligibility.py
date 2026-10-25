"""P1-02 conservative qualification rule tests, synthetic inputs only."""
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from bidowl.eligibility import evaluate_bid
from bidowl.profile import CompanyProfile
from bidowl.schema import Bid, Requirement

KST = timezone(timedelta(hours=9))
T0 = datetime(2026, 10, 26, 9, 0, 0, tzinfo=KST)


def requirement(kind="region_any", value=None, *, source_text="명시적 요건", source_locator="공고문 3쪽", rule_id="R1"):
    if value is None:
        value = ["부산광역시"]
    return Requirement(rule_id, kind, value, source_text, source_locator)


def bid(*rules, deadline=None):
    return Bid("DEMO-001", "합성 공고", "가상기관", "IT", deadline or T0 + timedelta(days=2), 20000000, tuple(rules), "DEMO_ONLY", T0, 2)


def profile(**kwargs):
    return CompanyProfile.from_mapping({"profile_id": "company-A", **kwargs})


class ProfileTests(unittest.TestCase):
    def test_missing_data_stays_missing(self):
        p = profile()
        self.assertIsNone(p.region)
        self.assertIsNone(p.licenses)
        self.assertIsNone(p.staff_count)

    def test_explicit_empty_means_known_empty(self):
        p = profile(licenses=[], categories=[], staff_count=0, experience_total_krw=0)
        self.assertEqual(p.licenses, ())
        self.assertEqual(p.staff_count, 0)

    def test_strict_profile_types(self):
        bad_profiles = [
            {"profile_id": ""}, {"profile_id": 12},
            {"region": " "}, {"region": 22},
            {"licenses": "면허"}, {"licenses": ["a", 4]}, {"licenses": ["a", "a"]},
            {"categories": ["", "IT"]},
            {"staff_count": True}, {"staff_count": -1}, {"staff_count": 1.5},
            {"experience_total_krw": False}, {"experience_total_krw": -1},
            {"unknown_field": 1}
        ]
        for value in bad_profiles:
            with self.subTest(value=value), self.assertRaises(ValueError):
                profile(**value)

    def test_missing_id_rejected(self):
        with self.assertRaises(ValueError):
            CompanyProfile.from_mapping({"region": "부산광역시"})

    def test_immutable_versioning(self):
        p1 = profile(region="부산광역시")
        p2 = replace(p1, region="서울특별시")
        self.assertEqual(p1.region, "부산광역시")
        self.assertEqual(p2.profile_id, p1.profile_id)


class EvaluatorTests(unittest.TestCase):
    def test_region_exact_pass(self):
        result = evaluate_bid(bid(requirement()), profile(region="부산광역시"), checked_at=T0)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.decisions[0].reason_code, "MATCH")
        self.assertEqual(result.decisions[0].source_text, "명시적 요건")
        self.assertEqual(result.decisions[0].source_locator, "공고문 3쪽")
        self.assertEqual(result.profile_id, "company-A")
        self.assertEqual(result.checked_at, T0)
        self.assertEqual(result.data_as_of, T0)
        self.assertFalse(result.is_expired)
        self.assertTrue(result.final_approval_required)
        self.assertFalse(result.requires_human_review)

    def test_region_fail_no_implicit_normalization(self):
        result = evaluate_bid(bid(requirement()), profile(region="부산"), checked_at=T0)
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.decisions[0].reason_code, "MISMATCH")

    def test_region_unknown_profile(self):
        result = evaluate_bid(bid(requirement()), profile(), checked_at=T0)
        self.assertEqual(result.status, "UNKNOWN")
        self.assertTrue(result.requires_human_review)
        self.assertEqual(result.decisions[0].reason_code, "PROFILE_MISSING")

    def test_license_all_pass_and_fail(self):
        rule = requirement("license_all", ["면허A", "면허B"])
        self.assertEqual(evaluate_bid(bid(rule), profile(licenses=["면허A", "면허B", "면허C"]), checked_at=T0).status, "PASS")
        self.assertEqual(evaluate_bid(bid(rule), profile(licenses=["면허A"]), checked_at=T0).status, "FAIL")

    def test_license_unknown_and_known_empty(self):
        rule = requirement("license_all", ["면허A"])
        self.assertEqual(evaluate_bid(bid(rule), profile(), checked_at=T0).status, "UNKNOWN")
        self.assertEqual(evaluate_bid(bid(rule), profile(licenses=[]), checked_at=T0).status, "FAIL")

    def test_category_overlap_and_disjoint(self):
        rule = requirement("category_any", ["IT", "교육"])
        self.assertEqual(evaluate_bid(bid(rule), profile(categories=["교육"]), checked_at=T0).status, "PASS")
        self.assertEqual(evaluate_bid(bid(rule), profile(categories=["행사"]), checked_at=T0).status, "FAIL")
        self.assertEqual(evaluate_bid(bid(rule), profile(categories=[]), checked_at=T0).status, "FAIL")

    def test_staff_inclusive_boundary(self):
        rule = requirement("staff_min", 3)
        self.assertEqual(evaluate_bid(bid(rule), profile(staff_count=3), checked_at=T0).status, "PASS")
        self.assertEqual(evaluate_bid(bid(rule), profile(staff_count=2), checked_at=T0).status, "FAIL")
        self.assertEqual(evaluate_bid(bid(rule), profile(), checked_at=T0).status, "UNKNOWN")

    def test_experience_inclusive_boundary(self):
        rule = requirement("experience_total_min_krw", 100000000)
        self.assertEqual(evaluate_bid(bid(rule), profile(experience_total_krw=100000000), checked_at=T0).status, "PASS")
        self.assertEqual(evaluate_bid(bid(rule), profile(experience_total_krw=0), checked_at=T0).status, "FAIL")
        self.assertEqual(evaluate_bid(bid(rule), profile(), checked_at=T0).status, "UNKNOWN")

    def test_source_text_missing_is_unknown_even_if_profile_passes(self):
        r = requirement(source_text=None)
        d = evaluate_bid(bid(r), profile(region="부산광역시"), checked_at=T0)
        self.assertEqual((d.status, d.decisions[0].reason_code), ("UNKNOWN", "SOURCE_MISSING"))

    def test_source_locator_missing_is_unknown_even_if_profile_fails(self):
        r = requirement(source_locator=None)
        d = evaluate_bid(bid(r), profile(region="서울특별시"), checked_at=T0)
        self.assertEqual((d.status, d.decisions[0].reason_code), ("UNKNOWN", "SOURCE_MISSING"))

    def test_unknown_kind_is_unknown(self):
        r = requirement("legal_interpretation", {"law": "uncertain"})
        d = evaluate_bid(bid(r), profile(region="부산광역시"), checked_at=T0)
        self.assertEqual((d.status, d.decisions[0].reason_code), ("UNKNOWN", "UNSUPPORTED_RULE"))

    def test_invalid_manual_rule_is_unknown(self):
        r = requirement("staff_min", True)
        d = evaluate_bid(bid(r), profile(staff_count=2), checked_at=T0)
        self.assertEqual((d.status, d.decisions[0].reason_code), ("UNKNOWN", "INVALID_RULE_VALUE"))

    def test_empty_or_missing_rules_is_unknown(self):
        d = evaluate_bid(bid(), profile(region="부산광역시"), checked_at=T0)
        self.assertEqual(d.status, "UNKNOWN")
        self.assertEqual(d.decisions, ())
        self.assertTrue(d.requires_human_review)

    def test_fail_dominates_unknown(self):
        r1 = requirement("region_any", ["서울특별시"], rule_id="r1")
        r2 = requirement("staff_min", 5, rule_id="r2")
        d = evaluate_bid(bid(r1, r2), profile(region="부산광역시"), checked_at=T0)
        self.assertEqual([r.status for r in d.decisions], ["FAIL", "UNKNOWN"])
        self.assertEqual(d.status, "FAIL")
        self.assertTrue(d.requires_human_review)  # unresolved rules still require follow-up

    def test_unknown_dominates_pass(self):
        r1 = requirement("region_any", ["부산광역시"], rule_id="r1")
        r2 = requirement("staff_min", 5, rule_id="r2")
        d = evaluate_bid(bid(r1, r2), profile(region="부산광역시"), checked_at=T0)
        self.assertEqual([r.status for r in d.decisions], ["PASS", "UNKNOWN"])
        self.assertEqual(d.status, "UNKNOWN")

    def test_every_rule_passes(self):
        r1 = requirement("region_any", ["부산광역시"], rule_id="r1")
        r2 = requirement("staff_min", 3, rule_id="r2")
        d = evaluate_bid(bid(r1, r2), profile(region="부산광역시", staff_count=3), checked_at=T0)
        self.assertEqual(d.status, "PASS")
        self.assertEqual(len(d.decisions), 2)
        self.assertTrue(all(r.status == "PASS" for r in d.decisions))

    def test_profile_change_recomputes(self):
        b = bid(requirement())
        before = evaluate_bid(b, profile(region="서울특별시"), checked_at=T0)
        after = evaluate_bid(b, profile(region="부산광역시"), checked_at=T0)
        self.assertEqual((before.status, after.status), ("FAIL", "PASS"))

    def test_deadline_is_independent_from_qualification(self):
        b = bid(requirement(), deadline=T0 - timedelta(seconds=1))
        d = evaluate_bid(b, profile(region="부산광역시"), checked_at=T0)
        self.assertEqual(d.status, "PASS")
        self.assertTrue(d.is_expired)

    def test_deadline_equal_is_expired(self):
        b = bid(requirement(), deadline=T0)
        self.assertTrue(evaluate_bid(b, profile(region="부산광역시"), checked_at=T0).is_expired)

    def test_naive_check_time_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_bid(bid(), profile(), checked_at=datetime(2026, 10, 26))

    def test_unknown_source_does_not_discard_other_rules(self):
        r1 = requirement(source_text=None, rule_id="r1")
        r2 = requirement("license_all", ["면허A"], rule_id="r2")
        d = evaluate_bid(bid(r1, r2), profile(licenses=[]), checked_at=T0)
        self.assertEqual([r.rule_id for r in d.decisions], ["r1", "r2"])
        self.assertEqual(d.status, "FAIL")

    def test_direct_invalid_profile_rejected(self):
        with self.assertRaises(ValueError):
            CompanyProfile(profile_id="x", staff_count=True)


if __name__ == "__main__":
    unittest.main()

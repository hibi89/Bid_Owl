import csv
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from bidowl import CSVImportError, load_csv, parse_csv
from bidowl.schema import MAX_CSV_BYTES


HEADERS = ["bid_no", "title", "agency", "category", "bid_deadline", "budget", "requirements", "source_ref", "data_as_of"]
RULE = {"id": "R-1", "kind": "license_all", "value": ["정보통신공사업"], "source": {"text": "정보통신공사업 등록", "locator": "공고문 3쪽"}}


def make_csv(*rows, headers=HEADERS, encoding="utf-8"):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return stream.getvalue().encode(encoding)


def row(no="2027-01", deadline="2027-11-01T17:00:00+09:00", budget="120000000", rules=None):
    return [no, "정보시스템 구축", "기관", "IT용역", deadline, budget, json.dumps([RULE] if rules is None else rules, ensure_ascii=False), "https://example.invalid/bid", "2026-10-26T02:00:00+09:00"]


class ImporterTests(unittest.TestCase):
    def test_utf8_bom_and_real_date(self):
        result = parse_csv(make_csv(row(), encoding="utf-8-sig"))
        self.assertTrue(result.ok, result.issues)
        self.assertEqual(result.bids[0].budget, 120000000)
        self.assertEqual(result.bids[0].requirements[0].source_locator, "공고문 3쪽")
        self.assertFalse(result.bids[0].is_expired(datetime(2026, 10, 26, tzinfo=timezone.utc)))

    def test_expired_is_flag_not_fake_import_error(self):
        result = parse_csv(make_csv(row(deadline="2025-08-10T09:00:00+09:00")))
        self.assertTrue(result.ok)
        self.assertTrue(result.bids[0].is_expired(datetime(2026, 10, 26, tzinfo=timezone.utc)))

    def test_duplicate_bid_no_rejects_batch(self):
        result = parse_csv(make_csv(row(), row()))
        self.assertIn("DUPLICATE_BID_NO", [e.code for e in result.issues])
        with self.assertRaises(CSVImportError):
            result.require_valid()

    def test_required_empty(self):
        r = row(); r[2] = ""
        self.assertIn("REQUIRED_EMPTY", [e.code for e in parse_csv(make_csv(r)).issues])

    def test_missing_header(self):
        self.assertIn("MISSING_COLUMN", [e.code for e in parse_csv(make_csv(row()[:5] + row()[6:], headers=HEADERS[:5] + HEADERS[6:])).issues])

    def test_extra_header(self):
        self.assertIn("UNKNOWN_COLUMN", [e.code for e in parse_csv(make_csv(row() + ["foo"], headers=HEADERS + ["unknown"])).issues])

    def test_duplicate_header(self):
        self.assertIn("DUPLICATE_COLUMN", [e.code for e in parse_csv(make_csv(row() + ["x"], headers=HEADERS + ["title"])).issues])

    def test_bad_budget(self):
        for value in ("0", "-1", "1.2", "10,000", "Infinity"):
            with self.subTest(value=value):
                self.assertIn("INVALID_BUDGET", [e.code for e in parse_csv(make_csv(row(budget=value))).issues])

    def test_bad_deadline_or_timezone(self):
        for value in ("2027-11-01", "2027-13-01T09:00:00+09:00", "2027-11-01T09:00:00", "2027-11-01T25:00:00+09:00"):
            with self.subTest(value=value):
                self.assertIn("INVALID_DEADLINE", [e.code for e in parse_csv(make_csv(row(deadline=value))).issues])

    def test_bad_json(self):
        r = row(); r[6] = "[broken"
        self.assertIn("INVALID_JSON", [e.code for e in parse_csv(make_csv(r)).issues])

    def test_duplicate_rule_id(self):
        self.assertIn("DUPLICATE_RULE_ID", [e.code for e in parse_csv(make_csv(row(rules=[RULE, RULE]))).issues])

    def test_invalid_known_rule_value(self):
        bad = dict(RULE, value="not-array")
        self.assertIn("INVALID_RULE_VALUE", [e.code for e in parse_csv(make_csv(row(rules=[bad]))).issues])

    def test_unknown_kind_retained_for_unknown_decision(self):
        r = dict(RULE, kind="law_interpretation")
        result = parse_csv(make_csv(row(rules=[r])))
        self.assertTrue(result.ok)
        self.assertEqual(result.bids[0].requirements[0].kind, "law_interpretation")

    def test_blank_source_retained_for_future_unknown(self):
        r = dict(RULE); r.pop("source")
        result = parse_csv(make_csv(row(rules=[r])))
        self.assertTrue(result.ok)
        self.assertIsNone(result.bids[0].requirements[0].source_text)

    def test_malformed_csv(self):
        data = (",".join(HEADERS) + '\n"never closed,foo\n').encode()
        self.assertIn("MALFORMED_CSV", [e.code for e in parse_csv(data).issues])

    def test_invalid_encoding(self):
        self.assertIn("INVALID_ENCODING", [e.code for e in parse_csv(b"\xff\xfe\xfa").issues])

    def test_column_count(self):
        self.assertIn("COLUMN_COUNT", [e.code for e in parse_csv(make_csv(row()[:-1])).issues])

    def test_empty_file_and_large_file(self):
        self.assertIn("EMPTY_FILE", [e.code for e in parse_csv(b" \n").issues])
        self.assertIn("FILE_TOO_LARGE", [e.code for e in parse_csv(b"x" * (MAX_CSV_BYTES + 1)).issues])

    def test_file_load_validation_and_no_partial_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bids.csv"
            path.write_bytes(make_csv(row()))
            self.assertEqual(len(load_csv(path)), 1)
            path.write_bytes(make_csv(row(), row()))
            with self.assertRaises(CSVImportError) as error:
                load_csv(path)
            self.assertEqual(error.exception.issues[0].code, "DUPLICATE_BID_NO")

    def test_missing_optional_columns_allowed(self):
        result = parse_csv(make_csv(row()[:7], headers=HEADERS[:7]))
        self.assertTrue(result.ok, result.issues)
        self.assertIsNone(result.bids[0].data_as_of)

    def test_timezone_naive_now_rejected(self):
        result = parse_csv(make_csv(row()))
        with self.assertRaises(ValueError):
            result.bids[0].is_expired(datetime(2026, 10, 26))


if __name__ == "__main__":
    unittest.main()

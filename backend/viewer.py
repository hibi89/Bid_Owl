"""BID OWL P2 read-only local SQLite browser (no remote server, no write API)."""
from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from bidowl.store import default_database_path

UI = Path(__file__).resolve().parent / "ui"
ALLOWED_FILES = {"/": ("index.html", "text/html; charset=utf-8"),
                 "/ui.css": ("ui.css", "text/css; charset=utf-8"),
                 "/ui.js": ("ui.js", "text/javascript; charset=utf-8")}
SECURITY = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"}


def open_database(path: Path) -> sqlite3.Connection:
    """SQLite URI mode=ro forbids mutations even from a future accidental SQL statement."""
    if not path.is_file():
        raise FileNotFoundError("SQLite file does not exist. Run cli.py to import CSV first.")
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    try:
        if conn.execute("PRAGMA user_version").fetchone()[0] != 1:
            raise ValueError("Unsupported SQLite schema version; expected BID OWL v1")
        required = {"bids", "bid_versions", "assessments", "rule_assessments", "profiles"}
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not required <= tables:
            raise ValueError("Not a complete BID OWL database")
    except BaseException:
        conn.close()
        raise
    return conn


def _timestamp(text: str | None) -> datetime | None:
    if not text:
        return None
    try:
        result = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return result if result.utcoffset() is not None else None
    except (TypeError, ValueError):
        return None


def _latest_rows(conn: sqlite3.Connection, profile_id: str = "", only_key: tuple[str, str] | None = None) -> list[dict]:
    # All selected user fields are parameter bound. Read-only connection is mandatory.
    rows = conn.execute("""
        SELECT b.source_id,b.bid_no,b.latest_version,v.payload,
               a.id assessment_id,a.status,a.checked_at,a.bid_version assessment_bid_version,
               a.profile_id,a.profile_version,a.requires_human_review,a.data_as_of assessment_data_as_of,
               p.latest_version latest_profile_version
          FROM bids b JOIN bid_versions v
            ON v.source_id=b.source_id AND v.bid_no=b.bid_no AND v.version=b.latest_version
          LEFT JOIN assessments a ON a.id=(
            SELECT x.id FROM assessments x
             WHERE x.source_id=b.source_id AND x.bid_no=b.bid_no
               AND (?='' OR x.profile_id=?) ORDER BY x.id DESC LIMIT 1)
          LEFT JOIN profiles p ON p.profile_id=a.profile_id
        {where_clause}
        ORDER BY b.source_id,b.bid_no
    """.format(where_clause="WHERE b.source_id=? AND b.bid_no=?" if only_key else ""),
        (profile_id, profile_id, *only_key) if only_key else (profile_id, profile_id)).fetchall()
    now = datetime.now(timezone.utc)
    result = []
    for row in rows:
        bid = json.loads(row["payload"])
        deadline = _timestamp(bid.get("bid_deadline"))
        fresh = bool(row["assessment_id"] and row["assessment_bid_version"] == row["latest_version"]
                     and row["profile_version"] == row["latest_profile_version"])
        status = row["status"] if fresh else "UNKNOWN"
        result.append({
            "source_id": row["source_id"], "bid_no": row["bid_no"], "title": bid.get("title", ""),
            "agency": bid.get("agency", ""), "category": bid.get("category", ""),
            "budget": bid.get("budget"), "deadline": bid.get("bid_deadline"),
            "data_as_of": bid.get("data_as_of"), "source_ref": bid.get("source_ref"),
            "bid_version": row["latest_version"], "expired": deadline is None or deadline <= now,
            "status": status, "snapshot_status": row["status"], "assessment_fresh": fresh,
            "assessment_id": row["assessment_id"], "checked_at": row["checked_at"],
            "profile_id": row["profile_id"],
            "requires_human_review": (not fresh or bool(row["requires_human_review"])),
            "review_reason": ("미판정" if row["assessment_id"] is None else
                              "원본 또는 회사 프로필 변경 후 재판정 필요" if not fresh else ""),
        })
    return result


def _arg(query: dict, name: str, default: str = "", *, max_length: int = 160) -> str:
    value = query.get(name, [default])
    if len(value) != 1 or not isinstance(value[0], str) or len(value[0]) > max_length:
        raise ValueError(f"Invalid query argument: {name}")
    return value[0].strip()


def query_bids(conn: sqlite3.Connection, query: dict, *, favorite_keys: set[tuple[str, str]] | None = None) -> dict:
    search = _arg(query, "q").casefold()
    if len(search) > 120:
        raise ValueError("Search is limited to 120 characters")
    category, status, deadline = [_arg(query, field) for field in ("category", "status", "deadline")]
    profile = _arg(query, "profile", max_length=300)
    if status not in ("", "PASS", "FAIL", "UNKNOWN") or deadline not in ("", "open", "expired"):
        raise ValueError("Unsupported filter")
    try:
        page = int(_arg(query, "page", "1"))
        page_size = int(_arg(query, "page_size", "30"))
    except ValueError as exc:
        raise ValueError("Page parameters must be integers") from exc
    if not 1 <= page <= 10000 or not 1 <= page_size <= 100:
        raise ValueError("Page parameters outside accepted range")
    rows = _latest_rows(conn, profile)
    categories = sorted({str(row["category"]) for row in rows if row["category"]})
    if favorite_keys is not None:
        rows = [r for r in rows if (r["source_id"], r["bid_no"]) in favorite_keys]
    if search:
        rows = [r for r in rows if search in " ".join(str(r[k]) for k in ("title","agency","bid_no","source_id")).casefold()]
    if category:
        rows = [r for r in rows if r["category"] == category]
    if status:
        rows = [r for r in rows if r["status"] == status]
    if deadline:
        rows = [r for r in rows if r["expired"] == (deadline == "expired")]
    rows.sort(key=lambda r: (r["expired"], r["deadline"] or "", r["source_id"], r["bid_no"]))
    total = len(rows)
    return {"items": rows[(page-1)*page_size:page*page_size], "total": total, "page": page,
            "page_size": page_size, "categories": categories, "generated_at": datetime.now(timezone.utc).isoformat(),
            "notice": "사용자 로컬 SQLite 조회. 자격 판정은 참고용이며 최종 공고 원문 확인 필수."}


def query_detail(conn: sqlite3.Connection, query: dict) -> dict:
    source_id, bid_no, profile = [
        _arg(query, field, max_length=300) for field in ("source_id", "bid_no", "profile")
    ]
    if not source_id or not bid_no:
        raise ValueError("source_id and bid_no required")
    row = next(iter(_latest_rows(conn, profile, (source_id, bid_no))), None)
    if row is None:
        raise LookupError("Bid not found")
    rules = []
    if row["assessment_id"]:
        for record in conn.execute("""SELECT rule_id,kind,status,reason_code,explanation,source_text,
            source_locator,requires_human_review FROM rule_assessments WHERE assessment_id=? ORDER BY position""",
            (row["assessment_id"],)):
            rules.append(dict(record))
    return {"bid": row, "rules": rules, "evidence_is_current": row["assessment_fresh"],
            "notice": "과거 평가 근거는 참고용. 버전이 바뀌면 재평가가 필요합니다."}


def query_profiles(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("SELECT profile_id,latest_version FROM profiles ORDER BY profile_id").fetchall()
    return {"profiles": [{"profile_id": r["profile_id"], "version": r["latest_version"]} for r in rows]}


def query_profile(conn: sqlite3.Connection, query: dict) -> dict:
    identifiers = query.get("profile_id", [])
    if len(identifiers) != 1 or not isinstance(identifiers[0], str):
        raise ValueError("Exactly one profile_id required")
    profile_id = identifiers[0]
    if not profile_id.strip() or len(profile_id) > 300:
        raise ValueError("Invalid profile_id")
    row = conn.execute("""SELECT v.payload,p.latest_version FROM profiles p
        JOIN profile_versions v ON p.profile_id=v.profile_id AND p.latest_version=v.version
        WHERE p.profile_id=?""", (profile_id,)).fetchone()
    if row is None:
        raise LookupError("Profile not found")
    profile = json.loads(row["payload"])
    return {"profile": profile, "version": row["latest_version"], "read_only": True}


MAX_REPORT_BYTES = 16 * 1024 * 1024


def render_saved_xlsx(conn: sqlite3.Connection, assessment_id: int) -> bytes:
    """Render historical XLSX in a self-cleaning temporary directory, DB read-only.

    No customer-selected filesystem path, output overwrite or HTTP mutation API.
    """
    if type(assessment_id) is not int or not 1 <= assessment_id <= 9223372036854775807:
        raise ValueError("Invalid assessment_id")
    from bidowl.report import load_review_report, write_xlsx
    from report_existing import SnapshotReader

    report = load_review_report(SnapshotReader(conn), assessment_id)
    with tempfile.TemporaryDirectory(prefix="bidowl-export-") as work:
        file = write_xlsx(report, Path(work) / "historical.xlsx")
        if file.stat().st_size > MAX_REPORT_BYTES:
            raise ValueError("Report exceeds maximum browser download size")
        return file.read_bytes()


MAX_FAVORITES = 1000
MAX_FAVORITES_BODY = 1024 * 1024
FAVORITE_FILTERS = {"q", "category", "status", "deadline", "profile", "page", "page_size"}


def query_favorites(conn: sqlite3.Connection, payload: object) -> dict:
    """A read-only bulk query; browser holds favorite IDs, not the user database."""
    if not isinstance(payload, dict) or set(payload) != {"favorites", "filters"}:
        raise ValueError("Expected favorites and filters")
    favorites, filters = payload["favorites"], payload["filters"]
    if (not isinstance(favorites, list) or len(favorites) > MAX_FAVORITES
            or not isinstance(filters, dict) or not set(filters) <= FAVORITE_FILTERS
            or any(type(value) is not str for value in filters.values())):
        raise ValueError("Invalid favorite query")
    keys = set()
    for pair in favorites:
        if (not isinstance(pair, list) or len(pair) != 2
                or any(type(item) is not str or not item.strip() or len(item) > 300 for item in pair)):
            raise ValueError("Invalid favorite identifier")
        keys.add((pair[0], pair[1]))
    return query_bids(conn, {key: [value] for key, value in filters.items()}, favorite_keys=keys)


class ViewerHandler(BaseHTTPRequestHandler):
    db_path: Path
    server_version = "BidOwlLocal/0.2"

    def _respond(self, status: int, content: bytes, content_type: str, *, download_name: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if download_name is not None:
            self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        for key, value in SECURITY.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _json(self, status: int, payload: dict) -> None:
        self._respond(status, json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        expected = {f"localhost:{self.server.server_port}", f"127.0.0.1:{self.server.server_port}"}
        host = self.headers.get("Host", "").lower()
        if host not in expected:
            self._json(403, {"error": "Forbidden host"})
            return
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://{host}"}:
            self._json(403, {"error": "Forbidden origin"})
            return
        # Three valid 300-character Korean identifiers can exceed 8 KiB
        # after percent encoding. Still cap the request target strictly.
        if len(self.path) > 12288:
            self._json(414, {"error": "URL too long"})
            return
        parsed = urlsplit(self.path)
        if parsed.path in ALLOWED_FILES and not parsed.query:
            filename, content_type = ALLOWED_FILES[parsed.path]
            try:
                self._respond(200, (UI / filename).read_bytes(), content_type)
            except OSError:
                self._json(500, {"error": "Missing bundled UI asset"})
            return
        if parsed.path not in ("/api/bids", "/api/detail", "/api/profiles", "/api/profile", "/api/report"):
            self._json(404, {"error": "Not found"})
            return
        try:
            query = parse_qs(parsed.query, keep_blank_values=True, max_num_fields=12, strict_parsing=False)
            if parsed.path == "/api/report":
                site = self.headers.get("Sec-Fetch-Site")
                if site is not None and site not in ("same-origin", "none"):
                    self._json(403, {"error": "Cross-site report download rejected"})
                    return
                if set(query) != {"assessment_id"}:
                    raise ValueError("Only assessment_id is supported for XLSX download")
                identifier = _arg(query, "assessment_id")
                if not identifier.isascii() or not identifier.isdecimal() or len(identifier) > 19:
                    raise ValueError("Invalid assessment_id")
                assessment_id = int(identifier)
                if not 1 <= assessment_id <= 9223372036854775807:
                    raise ValueError("Invalid assessment_id")
                with closing(open_database(self.db_path)) as conn:
                    content = render_saved_xlsx(conn, assessment_id)
                self._respond(200, content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    download_name=f"bidowl_review_{assessment_id:08d}.xlsx")
                return
            with closing(open_database(self.db_path)) as conn:
                if parsed.path == "/api/bids":
                    payload = query_bids(conn, query)
                elif parsed.path == "/api/detail":
                    payload = query_detail(conn, query)
                elif parsed.path == "/api/profile":
                    payload = query_profile(conn, query)
                else:
                    payload = query_profiles(conn)
            self._json(200, payload)
        except (ValueError, LookupError, KeyError) as exc:
            self._json(404 if isinstance(exc, (LookupError, KeyError)) else 400, {"error": str(exc)})
        except (sqlite3.Error, OSError, json.JSONDecodeError):
            self._json(500, {"error": "Local database cannot be read"})

    def do_POST(self) -> None:
        # POST carries a bounded list of IDs for a read-only query; it never writes.
        if self.path != "/api/bids/favorites":
            self._json(405, {"error": "Read-only viewer"})
            return
        host = self.headers.get("Host", "").lower()
        if host not in {f"localhost:{self.server.server_port}", f"127.0.0.1:{self.server.server_port}"}:
            self._json(403, {"error": "Forbidden host"})
            return
        if self.headers.get("Origin") != f"http://{host}":
            self._json(403, {"error": "Same-origin request required"})
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            self._json(415, {"error": "JSON required"})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._json(411, {"error": "Content-Length required"})
            return
        if not 0 < length <= MAX_FAVORITES_BODY:
            self._json(413, {"error": "Favorite request too large"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
            with closing(open_database(self.db_path)) as conn:
                data = query_favorites(conn, payload)
            self._json(200, data)
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except (sqlite3.Error, OSError):
            self._json(500, {"error": "Local database cannot be read"})

    def log_message(self, format: str, *args: object) -> None:
        # Do not echo URLs / user search terms / input records into external logs.
        pass


def make_server(path: Path, port: int) -> HTTPServer:
    if port < 0 or port > 65535:
        raise ValueError("port must be between 0 and 65535")
    with closing(open_database(path)):
        pass  # Fail before serving a missing or incompatible DB.
    handler = type("BoundViewerHandler", (ViewerHandler,), {"db_path": path})
    return HTTPServer(("127.0.0.1", port), handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL localhost read-only SQLite viewer")
    parser.add_argument("--db", type=Path, default=default_database_path(), help="Local BID OWL SQLite database")
    parser.add_argument("--port", type=int, default=8765, help="Local 127.0.0.1 port (0 for random)")
    args = parser.parse_args(argv)
    try:
        with make_server(args.db, args.port) as server:
            print(f"BID OWL LOCAL VIEWER: http://127.0.0.1:{server.server_port}", flush=True)
            server.serve_forever()
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"LOCAL_VIEWER_FAILED: {exc}")
        return 2
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
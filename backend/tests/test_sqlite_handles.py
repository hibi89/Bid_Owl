"""Prevent Windows WinError 32 regressions from unclosed SQLite context managers.

This AST audit does not touch any SQLite files and is OS-independent.
It catches direct `with sqlite3.connect(...)` or `with open_database(...)`;
Python's sqlite3.Connection.__exit__ does NOT close a connection.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def unclosed_sqlite_contexts(source: str, filename: str = "<synthetic>") -> list[str]:
    tree = ast.parse(source, filename=filename)
    violations: list[str] = []
    unsafe_factories = {"sqlite3.connect", "open_database", "viewer.open_database"}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.With, ast.AsyncWith)):
            continue
        for item in node.items:
            expression = item.context_expr
            if isinstance(expression, ast.Call) and _call_name(expression.func) in unsafe_factories:
                violations.append(f"{filename}:{expression.lineno}: {_call_name(expression.func)}")
    return violations


class SQLiteHandlePolicyTests(unittest.TestCase):
    def test_detects_bare_sqlite_context(self):
        src = "with sqlite3.connect('synthetic.sqlite3') as conn:\n    pass\n"
        self.assertEqual(unclosed_sqlite_contexts(src), ["<synthetic>:1: sqlite3.connect"])

    def test_detects_readonly_connection_context(self):
        src = "with open_database(Path('synthetic.sqlite3')) as conn:\n    pass\n"
        self.assertEqual(unclosed_sqlite_contexts(src), ["<synthetic>:1: open_database"])

    def test_accepts_explicit_closing_and_commit(self):
        src = ("with closing(sqlite3.connect('x')) as conn, conn:\n    pass\n"
               "with closing(open_database(Path('x'))) as view:\n    pass\n")
        self.assertEqual(unclosed_sqlite_contexts(src), [])

    def test_all_backend_sources_avoid_bare_sqlite_contexts(self):
        backend = Path(__file__).resolve().parent.parent
        scripts = sorted(backend.glob("*.py")) + sorted((backend / "bidowl").glob("*.py"))
        scripts += sorted((backend / "tests").glob("test_*.py"))
        self.assertGreaterEqual(len(scripts), 20, "Expected full backend checkout")
        violations: list[str] = []
        for script in scripts:
            violations.extend(unclosed_sqlite_contexts(
                script.read_text(encoding="utf-8"), str(script.relative_to(backend))
            ))
        self.assertEqual(violations, [], "Windows SQLite connection leak: use closing(...) explicitly")


if __name__ == "__main__":
    unittest.main()

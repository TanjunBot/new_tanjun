#!/usr/bin/env python3
"""Reject low-quality test patterns in CI."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

EXCEPT_PASS = re.compile(r"except Exception:\s*\n\s*pass", re.MULTILINE)
SHALLOW_MATRIX = re.compile(
    r"COMMAND_MATRIX_CASES[\s\S]{0,400}async def test_\w+_matrix",
    re.MULTILINE,
)


def main() -> int:
    failures: list[str] = []
    for path in sorted(TESTS.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if path.name.endswith("_generated.py"):
            failures.append(f"{rel}: *_generated.py must be migrated or deleted")
            continue
        text = path.read_text()
        if EXCEPT_PASS.search(text):
            failures.append(f"{rel}: contains 'except Exception: pass'")
        if SHALLOW_MATRIX.search(text):
            failures.append(f"{rel}: shallow COMMAND_MATRIX_CASES parametrization")
    if failures:
        print("lint_tests failed:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(f"lint_tests: OK ({len(list(TESTS.rglob('*.py')))} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

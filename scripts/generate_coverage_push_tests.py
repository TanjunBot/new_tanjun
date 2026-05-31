#!/usr/bin/env python3
"""Report coverage gaps for command modules — does not generate test files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERAGE_JSON = ROOT / "coverage.json"
MIN_PCT = 85.0


def failing_command_files() -> list[str]:
    if not COVERAGE_JSON.exists():
        raise SystemExit(f"{COVERAGE_JSON} missing — run pytest with --cov first")
    data = json.loads(COVERAGE_JSON.read_text())
    failing: list[str] = []
    for filepath, info in sorted(data.get("files", {}).items()):
        if not filepath.startswith("commands/"):
            continue
        summary = info.get("summary", {})
        total = summary.get("num_statements", 0)
        if total == 0:
            continue
        pct = summary.get("percent_covered", 0.0)
        if pct < MIN_PCT:
            failing.append(filepath)
    return failing


def main() -> None:
    failing = failing_command_files()
    if not failing:
        print(f"All command modules >= {MIN_PCT}% coverage")
        return
    print(f"{len(failing)} command module(s) below {MIN_PCT}%:\n")
    for path in failing:
        print(f"  - {path}")
    print("\nAdd hand-written integration tests; do not run codegen (*_generated.py).")
    sys.exit(1)


if __name__ == "__main__":
    main()

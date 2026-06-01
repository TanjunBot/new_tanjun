#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def check_per_file_coverage(coverage_json: Path, minimum: float) -> int:
    data = json.loads(coverage_json.read_text())
    files = data.get("files", {})
    failures: list[tuple[str, float, list[int]]] = []

    for filepath, info in sorted(files.items()):
        if "/tests/" in filepath or filepath.startswith("tests/"):
            continue
        if "/build/" in filepath or filepath.startswith("build/"):
            continue
        # Known low-coverage files tracked separately
        if _is_low_coverage_exception(filepath):
            continue
        summary = info.get("summary", {})
        covered = summary.get("covered_lines", 0)
        total = summary.get("num_statements", 0)
        if total == 0:
            continue
        pct = summary.get("percent_covered", 0.0)
        if pct < minimum:
            missing = sorted(info.get("missing_lines", []))
            failures.append((filepath, pct, missing))

    if failures:
        print(f"FAIL: {len(failures)} file(s) below {minimum}% coverage:\n")
        for filepath, pct, missing in failures:
            ranges = _line_ranges(missing[:50])
            suffix = f" (+{len(missing) - 50} more)" if len(missing) > 50 else ""
            print(f"  {filepath}: {pct:.1f}%  missing: {ranges}{suffix}")
        return 1

    print(f"PASS: all measured files >= {minimum}% coverage ({len(files)} files checked)")
    return 0


def _is_low_coverage_exception(filepath: str) -> bool:
    """Return True if filepath is a known low-coverage file exempt from per-file gate."""
    exemptions = {
        "commands/games/advanced_tic_tac_toe.py",
        "commands/games/battleship.py",
        "commands/games/memory.py",
        "commands/admin/copy_7tv_emote.py",
        "commands/admin/removetimeout.py",
        "commands/logs/blacklist_category/blacklist_list_category.py",
        "commands/logs/blacklist_voice/blacklist_list_voice.py",
        "commands/utility/report.py",
        "extensions/fun.py",
        "extensions/prometheus_metrics.py",
        "main.py",
        "localizer.py",
        "utils/exception_reporter.py",
    }
    # Normalize path suffixes so we match both absolute and relative paths
    for exc in exemptions:
        if filepath.endswith(exc):
            return True
    return False


def _line_ranges(lines: list[int]) -> str:
    if not lines:
        return "none"
    ranges: list[str] = []
    start = end = lines[0]
    for line in lines[1:]:
        if line == end + 1:
            end = line
        else:
            ranges.append(f"{start}-{end}" if start != end else str(start))
            start = end = line
    ranges.append(f"{start}-{end}" if start != end else str(start))
    return ", ".join(ranges)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail if any source file is below minimum coverage")
    parser.add_argument("--min", type=float, default=85.0, dest="minimum")
    parser.add_argument("--coverage-json", type=Path, default=Path("coverage.json"))
    args = parser.parse_args()

    if not args.coverage_json.exists():
        print(f"ERROR: {args.coverage_json} not found. Run pytest with --cov-report=json first.")
        return 1

    return check_per_file_coverage(args.coverage_json, args.minimum)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def identify_gaps(coverage_json: Path, minimum: float, top: int | None) -> int:
    data = json.loads(coverage_json.read_text())
    files = data.get("files", {})
    gaps: list[tuple[float, str, int, list[int]]] = []

    for filepath, info in files.items():
        if "/tests/" in filepath or filepath.startswith("tests/"):
            continue
        if "/build/" in filepath or filepath.startswith("build/"):
            continue
        summary = info.get("summary", {})
        total = summary.get("num_statements", 0)
        if total == 0:
            continue
        pct = summary.get("percent_covered", 0.0)
        if pct < minimum:
            missing = sorted(info.get("missing_lines", []))
            gaps.append((pct, filepath, total, missing))

    gaps.sort(key=lambda x: x[0])

    if top is not None:
        gaps = gaps[:top]

    if not gaps:
        print(f"All files >= {minimum}%")
        return 0

    print(f"{len(gaps)} file(s) below {minimum}%:\n")
    for pct, filepath, total, missing in gaps:
        print(f"  {filepath}: {pct:.1f}% ({total} stmts, {len(missing)} missing lines)")
        if missing:
            print(f"    lines: {missing[:30]}{'...' if len(missing) > 30 else ''}")

    return 1 if gaps else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, default=85.0)
    parser.add_argument("--coverage-json", type=Path, default=Path("coverage.json"))
    parser.add_argument("--top", type=int, default=None)
    parser.add_argument("--all", action="store_true", help="Show all failing files")
    args = parser.parse_args()

    top = None if args.all else (args.top or 20)
    if not args.coverage_json.exists():
        print(f"ERROR: {args.coverage_json} not found")
        return 1
    return identify_gaps(args.coverage_json, args.min, top)


if __name__ == "__main__":
    sys.exit(main())

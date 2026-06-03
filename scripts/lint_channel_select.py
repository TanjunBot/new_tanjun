#!/usr/bin/env python3
"""Reject unsafe ChannelSelect value handling patterns."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = (ROOT / "commands", ROOT / "extensions")
VALUES_PATTERN = re.compile(r"select\.values")
CAST_PATTERN = re.compile(r"cast\s*\(\s*discord\.TextChannel\s*,\s*select\.values")
PERMISSIONS_FOR_PATTERN = re.compile(r"\.permissions_for\s*\(")


def _line_violations(path: Path, line: str, line_no: int) -> list[str]:
    violations: list[str] = []
    if CAST_PATTERN.search(line):
        violations.append(f"{path.relative_to(ROOT)}:{line_no}: cast(discord.TextChannel, select.values...) hides AppCommandChannel")
    if VALUES_PATTERN.search(line) and PERMISSIONS_FOR_PATTERN.search(line):
        violations.append(f"{path.relative_to(ROOT)}:{line_no}: permissions_for used on same line as select.values")
    return violations


def _window_violations(path: Path, lines: list[str]) -> list[str]:
    violations: list[str] = []
    for index, line in enumerate(lines):
        if not VALUES_PATTERN.search(line):
            continue
        window = "".join(lines[index : index + 6])
        if PERMISSIONS_FOR_PATTERN.search(window) and "resolve_guild_channel" not in window:
            violations.append(
                f"{path.relative_to(ROOT)}:{index + 1}: permissions_for near select.values without resolve_guild_channel"
            )
    return violations


def main() -> int:
    failures: list[str] = []
    for base in SCAN_DIRS:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            text = path.read_text()
            lines = text.splitlines()
            for line_no, line in enumerate(lines, start=1):
                failures.extend(_line_violations(path, line, line_no))
            failures.extend(_window_violations(path, lines))
    failures = sorted(set(failures))
    if failures:
        print("lint_channel_select failed:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print("lint_channel_select: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

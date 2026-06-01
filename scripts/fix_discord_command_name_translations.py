#!/usr/bin/env python3
"""Normalize command/option name translations for Discord slash command rules."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LOCALE_DIR = Path(__file__).resolve().parent.parent / "locales"
NAME_LABELS = frozenset({"command_name", "command_option_name"})


def normalize_discord_command_name(name: str) -> str | None:
    normalized = re.sub(r"\s+", "_", name.strip().lower())
    normalized = re.sub(r"[^\w\-]", "", normalized, flags=re.UNICODE)
    if not normalized:
        return None
    return normalized[:32]


def fix_locale_file(path: Path, *, dry_run: bool) -> int:
    data: list[dict[str, object]] = json.loads(path.read_text(encoding="utf-8"))
    changed = 0

    for entry in data:
        labels_raw = entry.get("labels") or ""
        labels = {part.strip() for part in str(labels_raw).split(",") if part.strip()}
        if not labels & NAME_LABELS:
            continue

        translation = str(entry.get("translation", ""))
        normalized = normalize_discord_command_name(translation)
        if normalized is None or normalized == translation:
            continue

        if not dry_run:
            entry["translation"] = normalized
            source = entry.get("source_string")
            if source is not None and str(source) == translation:
                entry["source_string"] = normalized

        changed += 1

    if changed and not dry_run:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing files")
    args = parser.parse_args()

    total = 0
    for path in sorted(LOCALE_DIR.glob("*.json")):
        count = fix_locale_file(path, dry_run=args.dry_run)
        if count:
            print(f"{path.name}: {count}")
            total += count

    print(f"total: {total}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fail if diagnostics/manifest.json does not match the current command tree."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagnostics.tree import MANIFEST_PATH, compare_tree_to_manifest
from tests.helpers.extension_loader import fire_cog_on_ready, load_all_extensions, make_bot_for_extensions


async def _build_bot():
    bot = make_bot_for_extensions()
    await load_all_extensions(bot)
    await fire_cog_on_ready(bot)
    return bot


def _print_set_diff(label: str, missing: set[str], extra: set[str]) -> None:
    if missing:
        print(f"Missing {label}:", file=sys.stderr)
        for item in sorted(missing)[:20]:
            print(f"  - {item}", file=sys.stderr)
    if extra:
        print(f"Extra {label}:", file=sys.stderr)
        for item in sorted(extra)[:20]:
            print(f"  + {item}", file=sys.stderr)


def main() -> int:
    if not MANIFEST_PATH.is_file():
        print(f"Missing {MANIFEST_PATH}; run scripts/generate_diagnostics_manifest.py", file=sys.stderr)
        return 1

    bot = asyncio.run(_build_bot())
    missing, extra, missing_sub, extra_sub = compare_tree_to_manifest(bot)

    if missing or extra or missing_sub or extra_sub:
        _print_set_diff("paths in tree", missing, extra)
        _print_set_diff("minigame subgroups", missing_sub, extra_sub)
        return 1

    print("diagnostics manifest OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

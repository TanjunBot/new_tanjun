#!/usr/bin/env python3
"""Fail if diagnostics/manifest.json does not match the current command tree."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.mock_config as mock_config

mock_config.patch_config_module()

from diagnostics.tree import MANIFEST_PATH, compare_tree_to_manifest
from tests.helpers.extension_loader import build_extension_bot, teardown_extension_bot


def _print_set_diff(label: str, missing: set[str], extra: set[str]) -> None:
    if missing:
        print(f"Missing {label}:", file=sys.stderr)
        for item in sorted(missing)[:20]:
            print(f"  - {item}", file=sys.stderr)
    if extra:
        print(f"Extra {label}:", file=sys.stderr)
        for item in sorted(extra)[:20]:
            print(f"  + {item}", file=sys.stderr)


async def _check_manifest() -> int:
    if not MANIFEST_PATH.is_file():
        print(f"Missing {MANIFEST_PATH}; run scripts/generate_diagnostics_manifest.py", file=sys.stderr)
        return 1

    bot = await build_extension_bot()
    try:
        missing, extra, missing_sub, extra_sub = compare_tree_to_manifest(bot)
    finally:
        await teardown_extension_bot(bot)

    if missing or extra or missing_sub or extra_sub:
        _print_set_diff("paths in tree", missing, extra)
        _print_set_diff("minigame subgroups", missing_sub, extra_sub)
        return 1

    print("diagnostics manifest OK")
    return 0


def main() -> int:
    return asyncio.run(_check_manifest())


if __name__ == "__main__":
    raise SystemExit(main())

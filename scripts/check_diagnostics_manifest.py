#!/usr/bin/env python3
"""Fail if diagnostics/manifest.json does not match the current command tree."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagnostics.tree import MANIFEST_PATH, collect_tree_paths
from tests.helpers.extension_loader import fire_cog_on_ready, load_all_extensions, make_bot_for_extensions


async def _actual() -> dict[str, object]:
    bot = make_bot_for_extensions()
    await load_all_extensions(bot)
    await fire_cog_on_ready(bot)
    roots = sorted({getattr(cmd, "name", str(cmd)) for cmd in bot.tree.get_commands()})
    paths = sorted(collect_tree_paths(bot))
    return {"roots": roots, "paths": paths}


def main() -> int:
    if not MANIFEST_PATH.is_file():
        print(f"Missing {MANIFEST_PATH}; run scripts/generate_diagnostics_manifest.py", file=sys.stderr)
        return 1
    expected = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    actual = asyncio.run(_actual())
    if expected.get("paths"):
        exp_paths = set(expected["paths"])
        act_paths = set(actual["paths"])
        if exp_paths != act_paths:
            missing = exp_paths - act_paths
            extra = act_paths - exp_paths
            if missing:
                print("Missing paths in tree:", file=sys.stderr)
                for p in sorted(missing)[:20]:
                    print(f"  - {p}", file=sys.stderr)
            if extra:
                print("Extra paths in tree:", file=sys.stderr)
                for p in sorted(extra)[:20]:
                    print(f"  + {p}", file=sys.stderr)
            return 1
    else:
        exp_roots = set(expected.get("roots") or [])
        act_roots = set(actual.get("roots") or [])
        if exp_roots != act_roots:
            print(f"Root mismatch expected={exp_roots} actual={act_roots}", file=sys.stderr)
            return 1
    print("diagnostics manifest OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

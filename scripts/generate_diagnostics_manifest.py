#!/usr/bin/env python3
"""Generate diagnostics/manifest.json from the live command tree on a mock bot."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.mock_config as mock_config

mock_config.patch_config_module()

from diagnostics.tree import MANIFEST_PATH, collect_tree_paths, iter_tree_paths
from tests.helpers.extension_loader import fire_cog_on_ready, load_all_extensions, make_bot_for_extensions


async def _build_manifest() -> dict[str, object]:
    bot = make_bot_for_extensions()
    await load_all_extensions(bot)
    await fire_cog_on_ready(bot)
    roots = sorted({getattr(cmd, "name", str(cmd)) for cmd in bot.tree.get_commands()})
    paths = sorted(collect_tree_paths(bot))
    minigame_subgroups: list[str] = []
    for cmd in bot.tree.get_commands():
        if getattr(cmd, "name", None) == "minigame_name":
            minigame_subgroups = sorted(getattr(c, "name", str(c)) for c in getattr(cmd, "commands", []))
            break
    return {"roots": roots, "paths": paths, "minigame_subgroups": minigame_subgroups}


def main() -> int:
    manifest = asyncio.run(_build_manifest())
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH} ({len(manifest.get('paths', []))} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"


def iter_tree_paths(commands_list: list[Any], prefix: tuple[str, ...] = ()) -> Iterator[tuple[str, ...]]:
    for cmd in commands_list:
        name = getattr(cmd, "name", None)
        if not name:
            continue
        path = (*prefix, str(name))
        children = list(getattr(cmd, "commands", []) or [])
        if children:
            yield from iter_tree_paths(children, path)
        else:
            yield path


def collect_tree_paths(bot: Any) -> set[str]:
    tree = getattr(bot, "tree", None)
    if tree is None:
        return set()
    roots = tree.get_commands()
    return {" ".join(path) for path in iter_tree_paths(list(roots))}


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        return {"roots": [], "paths": [], "minigame_subgroups": []}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def compare_tree_to_manifest(bot: Any) -> tuple[set[str], set[str]]:
    manifest = load_manifest()
    expected_paths = set(manifest.get("paths") or [])
    if not expected_paths:
        expected_roots = set(manifest.get("roots") or [])
        actual_roots = {getattr(c, "name", "") for c in (bot.tree.get_commands() if bot.tree else [])}
        missing = expected_roots - actual_roots
        extra = actual_roots - expected_roots
        return missing, extra
    actual = collect_tree_paths(bot)
    return expected_paths - actual, actual - expected_paths

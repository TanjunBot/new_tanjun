#!/usr/bin/env python3
from __future__ import annotations

import ast
import inspect
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from diagnostics.tree import load_manifest
from tests.helpers.command_coverage.inventory import (
    detect_permission_checks_for_paths,
    manifest_paths,
    tree_path_for_command_module,
)

PERMISSION_FULL = ["admin", "member", "restricted", "no_guild", "channel_deny_send", "channel_deny_embed"]
PERMISSION_BASIC = ["admin", "restricted"]
LOCALES = ["en-US", "de", "fr"]
MESSAGE_KINDS = ["none", "empty", "short", "unicode", "max", "multiline"]
E2E_MESSAGE_KINDS = ["none", "short", "unicode", "max"]
TARGETS = ["self", "bot"]
EXPRESSIONS = ["valid", "invalid"]
PROMPT_KINDS = ["short", "empty"]
ATTACHMENTS = ["present"]
OUTCOMES = ["success", "denied"]


def _handler_for_path(tree_path: str) -> ast.AsyncFunctionDef | None:
    import json as _json

    handlers = _json.loads((ROOT / "coverage" / "command_handlers.json").read_text(encoding="utf-8"))
    handler_path = handlers.get("by_path", {}).get(tree_path)
    if not handler_path:
        return None
    module_path, func_name = handler_path.rsplit(".", 1)
    rel = module_path.replace("commands.", "").replace(".", "/") + ".py"
    path = ROOT / "commands" / rel
    if not path.is_file():
        return None
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            return node
    return None


def _param_names(handler: ast.AsyncFunctionDef | None) -> set[str]:
    if handler is None:
        return set()
    return {arg.arg for arg in handler.args.args}


def classify_path(tree_path: str, permission_paths: dict[str, bool]) -> dict[str, list[str]]:
    dims: dict[str, list[str]] = {}
    handler = _handler_for_path(tree_path)
    params = _param_names(handler)
    if permission_paths.get(tree_path):
        dims["permission"] = PERMISSION_FULL
    else:
        dims["permission"] = PERMISSION_BASIC
    if params & {"user", "member", "target", "opponent", "player"}:
        dims["target"] = TARGETS
    if params & {"message", "content"}:
        dims["message_kind"] = MESSAGE_KINDS
    if params & {"locale", "language"}:
        dims["locale"] = LOCALES
    if params & {"equation", "expression", "func", "func_str"}:
        dims["expression"] = EXPRESSIONS
    if params & {"prompt", "situation"}:
        dims["prompt_kind"] = PROMPT_KINDS
    if params & {"image", "attachment"}:
        dims["attachment"] = ATTACHMENTS
    if params & {"theme", "size"}:
        if "theme" in params:
            dims["theme"] = ["characters", "flags"]
        if "size" in params:
            dims["size"] = ["small", "medium", "large"]
    return dims


def classify_group(root: str, paths: list[str], permission_paths: dict[str, bool]) -> dict[str, Any]:
    if root == "funcmd_name":
        return {}
    per_path_dims: list[dict[str, list[str]]] = [classify_path(p, permission_paths) for p in paths]
    merged: dict[str, set[str]] = {}
    for dims in per_path_dims:
        for key, values in dims.items():
            merged.setdefault(key, set()).update(values)
    dimensions = {k: sorted(v) for k, v in merged.items()}
    if not dimensions:
        dimensions = {"permission": PERMISSION_BASIC}
    unit_axes = list(dimensions.keys())
    e2e_axes = ["permission", "target", "message_kind"]
    e2e_overrides: dict[str, list[str]] = {
        "permission": ["admin"],
        "target": TARGETS,
        "message_kind": E2E_MESSAGE_KINDS,
    }
    if "locale" in dimensions:
        e2e_axes = ["permission", "locale"]
        e2e_overrides = {"permission": ["admin"], "locale": LOCALES}
    if "expression" in dimensions:
        e2e_axes = ["permission", "expression", "target"]
        e2e_overrides = {"permission": ["admin"], "expression": EXPRESSIONS, "target": TARGETS}
    if "prompt_kind" in dimensions:
        e2e_axes = ["permission", "prompt_kind"]
        e2e_overrides = {"permission": ["admin", "restricted"], "prompt_kind": PROMPT_KINDS}
    if "attachment" in dimensions:
        e2e_axes = ["permission", "attachment", "target"]
        e2e_overrides = {"permission": ["admin"], "attachment": ATTACHMENTS, "target": TARGETS}
    layers: dict[str, Any] = {
        "unit_logic": [{"axes": unit_axes, "per_path": True}],
        "integration": [
            {
                "axes": [a for a in unit_axes if a != "locale"],
                "per_path": True,
                "overrides": {"permission": PERMISSION_FULL if permission_paths.get(paths[0]) else PERMISSION_BASIC},
            }
        ],
        "behavior_spec": [{"axes": [], "per_path": True}],
        "e2e_live": [{"axes": e2e_axes, "per_path": True, "overrides": e2e_overrides}],
    }
    if len(paths) == 1 and paths[0] == root:
        return {"tree_paths": paths, "dimensions": dimensions, "per_path": False, "layers": layers}
    return {"tree_paths": paths, "dimensions": dimensions, "per_path": True, "layers": layers}


def main() -> None:
    manifest = load_manifest()
    permission_paths = detect_permission_checks_for_paths()
    groups: dict[str, Any] = {}
    for root in manifest["roots"]:
        paths = [p for p in manifest["paths"] if p.startswith(root + " ") or p == root]
        if root == "funcmd_name":
            continue
        groups[root] = classify_group(root, paths, permission_paths)
    out = ROOT / "coverage" / "axis_classification.json"
    out.write_text(json.dumps(groups, indent=2), encoding="utf-8")
    print(f"Classified {len(groups)} groups -> {out}")


if __name__ == "__main__":
    main()

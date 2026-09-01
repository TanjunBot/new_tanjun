from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

from diagnostics.tree import load_manifest
from tests.helpers.command_coverage.models import CommandInventoryEntry

ROOT = Path(__file__).resolve().parents[3]
COMMANDS_DIR = ROOT / "commands"

PERMISSION_MARKERS = (
    "can_moderate",
    "check_user_permission",
    "check_bot_permission",
    "send_check_failure",
    "require_moderate_members",
    "require_bot_permissions",
    "check_executor_hierarchy",
    "check_bot_hierarchy",
)


def manifest_paths() -> list[str]:
    manifest = load_manifest()
    return list(manifest.get("paths") or [])


def manifest_roots() -> list[str]:
    manifest = load_manifest()
    return list(manifest.get("roots") or [])


def root_group_for_path(tree_path: str) -> str:
    return tree_path.split(" ", 1)[0]


def leaf_name_for_path(tree_path: str) -> str:
    return tree_path.rsplit(" ", 1)[-1]


def _has_permission_checks(command_file: Path) -> bool:
    try:
        source = command_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in PERMISSION_MARKERS:
                return True
    return False


def _command_file_for_module(mod_path: str) -> Path | None:
    rel = mod_path.replace("commands.", "").replace(".", "/") + ".py"
    path = COMMANDS_DIR / rel
    return path if path.is_file() else None


def _infer_param_variants(handler: Any) -> dict[str, list[str]]:
    params: dict[str, list[str]] = {}
    try:
        sig = inspect.signature(handler)
    except (TypeError, ValueError):
        return params
    for name, param in sig.parameters.items():
        if name in ("self", "interaction", "ctx"):
            continue
        if param.default is inspect.Parameter.empty:
            params[name] = ["sample"]
        else:
            params[name] = ["none", "sample"]
    return params


def tree_path_for_command_module(mod_path: str, func_name: str, paths: list[str] | None = None) -> str | None:
    paths = paths or manifest_paths()
    candidates = [
        path
        for path in paths
        if path.endswith(f"_{func_name}_name") or path.rsplit(" ", 1)[-1] == func_name
    ]
    if len(candidates) == 1:
        return candidates[0]
    mod_tail = mod_path.rsplit(".", 1)[-1]
    narrowed = [path for path in candidates if f"_{mod_tail}_" in path or path.endswith(f"_{mod_tail}_name")]
    if len(narrowed) == 1:
        return narrowed[0]
    if candidates:
        return sorted(candidates)[0]
    return None


def build_inventory() -> list[CommandInventoryEntry]:
    paths = manifest_paths()
    entries: list[CommandInventoryEntry] = []
    for tree_path in paths:
        root = root_group_for_path(tree_path)
        entries.append(
            CommandInventoryEntry(
                tree_path=tree_path,
                root_group=root,
            )
        )
    return entries


def enrich_inventory_from_specs(
    entries: list[CommandInventoryEntry],
    specs: list[Any],
) -> list[CommandInventoryEntry]:
    by_path = {entry.tree_path: entry for entry in entries}
    for spec in specs:
        if not spec.tree_path:
            continue
        entry = by_path.get(spec.tree_path)
        if entry is None:
            continue
        by_path[spec.tree_path] = CommandInventoryEntry(
            tree_path=entry.tree_path,
            root_group=entry.root_group,
            extension=spec.extension,
            method_name=spec.method_name,
            has_permission_checks=entry.has_permission_checks,
            parameters=entry.parameters,
        )
    return list(by_path.values())


def detect_permission_checks_for_paths() -> dict[str, bool]:
    result: dict[str, bool] = {}
    paths = manifest_paths()
    for command_file in COMMANDS_DIR.rglob("*.py"):
        if command_file.name.startswith("_") or command_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(command_file.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        mod_path = "commands." + ".".join(command_file.relative_to(COMMANDS_DIR).with_suffix("").parts)
        has_checks = _has_permission_checks(command_file)
        for node in tree.body:
            if not isinstance(node, ast.AsyncFunctionDef):
                continue
            if not any(arg.arg in ("command_info", "info") for arg in node.args.args):
                continue
            tree_path = tree_path_for_command_module(mod_path, node.name, paths)
            if tree_path and has_checks:
                result[tree_path] = True
    return result

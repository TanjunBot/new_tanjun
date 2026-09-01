#!/usr/bin/env python3
"""Reject view transitions that attach a paginated view without rendering its initial embed."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = (ROOT / "commands", ROOT / "extensions")
RENDER_MARKERS = ("_render_embed", "render_for_message", "get_embed")
EMBED_CALLEES = frozenset({"tanjunEmbed", "utility.tanjunEmbed"})


def _paginated_view_classes(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name in RENDER_MARKERS:
                names.add(node.name)
                break
    return names


def _call_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


def _is_static_embed(node: ast.expr) -> bool:
    if isinstance(node, ast.Call):
        return _is_static_embed(node.func)
    name = _call_name(node)
    return name in EMBED_CALLEES


def _function_violations(path: Path, func: ast.AsyncFunctionDef | ast.FunctionDef, paginated_views: set[str]) -> list[str]:
    if not paginated_views:
        return []
    body = ast.walk(func)
    has_render = any(
        isinstance(n, ast.Call)
        and (
            (isinstance(n.func, ast.Attribute) and n.func.attr in RENDER_MARKERS)
            or (_call_name(n.func) or "").endswith(tuple(RENDER_MARKERS))
        )
        for n in body
    )
    if has_render:
        return []

    new_view_vars: set[str] = set()
    static_embed_vars: set[str] = set()
    violations: list[str] = []

    for node in func.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            callee = _call_name(node.value.func)
            if callee in paginated_views:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        new_view_vars.add(target.id)
            if _is_static_embed(node.value):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        static_embed_vars.add(target.id)

        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Await):
            continue
        call = node.value.value
        if not isinstance(call, ast.Call):
            continue
        callee = _call_name(call.func)
        if callee is None or not callee.endswith("edit_message"):
            continue
        embed_arg: ast.expr | None = None
        view_arg: ast.expr | None = None
        for kw in call.keywords:
            if kw.arg == "embed":
                embed_arg = kw.value
            elif kw.arg == "view":
                view_arg = kw.value
        if embed_arg is None or view_arg is None:
            continue
        static_embed = _is_static_embed(embed_arg) or (
            isinstance(embed_arg, ast.Name) and embed_arg.id in static_embed_vars
        )
        if not static_embed:
            continue
        view_name: str | None = None
        if isinstance(view_arg, ast.Name):
            view_name = view_arg.id
        elif isinstance(view_arg, ast.Call):
            view_name = _call_name(view_arg.func)
        if view_name is None:
            continue
        if view_name in new_view_vars or view_name in paginated_views:
            violations.append(
                f"{path.relative_to(ROOT)}:{node.lineno}: edit_message uses static embed with "
                f"paginated view {view_name!r} without calling {', '.join(RENDER_MARKERS)}"
            )
    return violations


def _file_violations(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return []
    if not isinstance(tree, ast.Module):
        return []
    paginated_views = _paginated_view_classes(tree)
    failures: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            failures.extend(_function_violations(path, node, paginated_views))
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.AsyncFunctionDef, ast.FunctionDef)):
                    failures.extend(_function_violations(path, child, paginated_views))
    return failures


def main() -> int:
    failures: list[str] = []
    for base in SCAN_DIRS:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            failures.extend(_file_violations(path))
    failures = sorted(set(failures))
    if failures:
        print("lint_view_initial_embed failed:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print("lint_view_initial_embed: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

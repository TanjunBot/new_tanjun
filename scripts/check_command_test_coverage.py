#!/usr/bin/env python3
"""Verify integration tests exist for command handler modules."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / "commands"
TESTS_DIR = ROOT / "tests" / "integration" / "commands"


def _is_command_module(path: Path) -> bool:
    if path.name.startswith("_") or path.name == "__init__.py":
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            if any(arg.arg == "command_info" for arg in node.args.args):
                return True
    return False


def _module_path(command_file: Path) -> str:
    rel = command_file.relative_to(COMMANDS_DIR).with_suffix("")
    return "commands." + ".".join(rel.parts)


def _has_matching_test(module_path: str, stem: str, parent: Path) -> bool:
    direct = TESTS_DIR / parent / f"test_{stem}.py"
    if direct.is_file():
        return True
    needles = (module_path, module_path.replace(".", "/"), f"from {module_path}", f"import {module_path}")
    for test_file in TESTS_DIR.rglob("test_*.py"):
        text = test_file.read_text(encoding="utf-8")
        if any(n in text for n in needles):
            return True
    return False


def main() -> int:
    missing: list[str] = []
    for command_file in sorted(COMMANDS_DIR.rglob("*.py")):
        if not _is_command_module(command_file):
            continue
        rel_parent = command_file.relative_to(COMMANDS_DIR).parent
        module_path = _module_path(command_file)
        if not _has_matching_test(module_path, command_file.stem, rel_parent):
            missing.append(module_path)
    if missing:
        print("Command modules without integration test coverage:", file=sys.stderr)
        for mod in missing:
            print(f"  - {mod}", file=sys.stderr)
        return 1
    covered = sum(1 for p in COMMANDS_DIR.rglob("*.py") if _is_command_module(p))
    print(f"All {covered} command handler modules have integration test coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

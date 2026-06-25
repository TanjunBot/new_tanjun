from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.command_coverage.inventory import tree_path_for_command_module
from tests.helpers.command_coverage.models import AssertionDepth, CoverageCell, LayerKind

ROOT = Path(__file__).resolve().parents[4]
INTEGRATION_COMMANDS = ROOT / "tests" / "integration" / "commands"

FIXTURE_TO_PERMISSION = {
    "admin_command_info": "admin",
    "restricted_command_info": "restricted",
    "no_guild_command_info": "no_guild",
    "member_command_info": "member",
}

NAME_TO_PERMISSION = {
    "admin": "admin",
    "restricted": "restricted",
    "no_guild": "no_guild",
    "member": "member",
}


def _permission_from_test_name(name: str) -> str | None:
    lowered = name.lower()
    for token, permission in NAME_TO_PERMISSION.items():
        if token in lowered:
            return permission
    return None


def _permission_from_fixture(name: str) -> str | None:
    return FIXTURE_TO_PERMISSION.get(name)


def _extract_imports(tree: ast.Module) -> list[tuple[str, str]]:
    imports: list[tuple[str, str]] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("commands."):
            for alias in node.names:
                if alias.name == "__init__":
                    continue
                imports.append((node.module, alias.asname or alias.name))
    return imports


def _extract_profile_cases(tree: ast.Module) -> list[tuple[str, str, str]]:
    cases: list[tuple[str, str, str]] = []
    mod_path = ""
    func_name = ""

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if (
                node.func.attr == "from_module"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "CommandProfile"
                and len(node.args) >= 2
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[1], ast.Constant)
            ):
                mod_path = str(node.args[0].value)
                func_name = str(node.args[1].value)

    if mod_path and func_name:
        matrix_cases: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "assert_matrix_outcome" and len(node.args) >= 2:
                    if isinstance(node.args[1], ast.Constant):
                        matrix_cases.add(str(node.args[1].value))
        if not matrix_cases:
            matrix_cases = {"admin"}
        for case in sorted(matrix_cases):
            cases.append((mod_path, func_name, case))
        return cases

    for mod_path, func_name in _extract_imports(tree):
        for node in tree.body:
            if not isinstance(node, ast.AsyncFunctionDef) or not node.name.startswith("test_"):
                continue
            permission = _permission_from_test_name(node.name)
            if permission is None:
                for arg in node.args.args:
                    permission = _permission_from_fixture(arg.arg)
                    if permission:
                        break
            if permission is None:
                permission = "admin"
            cases.append((mod_path, func_name, permission))

    return cases


def collect_integration_profile_cells() -> list[CoverageCell]:
    cells: list[CoverageCell] = []
    if not INTEGRATION_COMMANDS.is_dir():
        return cells

    seen: set[tuple[str, str, str]] = set()
    for test_file in INTEGRATION_COMMANDS.rglob("test_*.py"):
        try:
            tree = ast.parse(test_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for mod_path, func_name, permission in _extract_profile_cases(tree):
            tree_path = tree_path_for_command_module(mod_path, func_name)
            if not tree_path:
                continue
            key = (tree_path, permission, str(test_file))
            if key in seen:
                continue
            seen.add(key)
            cells.append(
                CoverageCell(
                    tree_path=tree_path,
                    layer=LayerKind.INTEGRATION,
                    dimensions={"permission": permission},
                    assertion_depth=AssertionDepth.OUTCOME,
                    source=str(test_file.relative_to(ROOT)),
                )
            )
    return cells

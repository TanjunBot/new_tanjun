from __future__ import annotations

import importlib
import json
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from diagnostics.harness import invoke_interaction_command
from tests.helpers.command_matrix.dimensions import kwargs_for_matrix_case
from tests.helpers.command_matrix.harness import permission_for_case
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.resolver import resolve_command_callable
from tests.helpers.permission_profiles import command_info_for_permission

ROOT = Path(__file__).resolve().parents[3]
_HANDLERS_JSON = ROOT / "coverage" / "command_handlers.json"


def _load_path_meta(tree_path: str) -> dict[str, str] | None:
    if not _HANDLERS_JSON.is_file():
        return None
    data = json.loads(_HANDLERS_JSON.read_text(encoding="utf-8"))
    return (data.get("path_meta") or {}).get(tree_path)


async def run_integration_matrix_case(case: MatrixCase) -> None:
    meta = _load_path_meta(case.tree_path)
    if meta is None:
        pytest.fail(f"No path metadata for integration case {case.id}")

    command_fn = resolve_command_callable(case.tree_path)
    if command_fn is None:
        pytest.fail(f"No command handler for integration case {case.id}")

    extension = meta.get("extension")
    group_ref = meta.get("group_cls")
    method_name = meta.get("method")
    if not extension or not group_ref or not method_name:
        pytest.fail(f"Incomplete path metadata for {case.id}")

    from diagnostics.patches import extension_patches
    from tests.integration.extensions.conftest import load_extension_bot

    group_module, group_cls_name = group_ref.rsplit(".", 1)
    group_cls = getattr(importlib.import_module(group_module), group_cls_name)
    bot = await load_extension_bot(extension)
    group = group_cls(name="diag", description="diag") if hasattr(group_cls, "name") else group_cls()
    handler = getattr(group, method_name, None)
    if handler is None:
        pytest.fail(f"Handler {method_name!r} missing for {case.id}")

    extra = kwargs_for_matrix_case(case)
    if case.dimension("permission"):
        profile = permission_for_case(case)
        extra["user"] = command_info_for_permission(profile).user

    patch_target = meta.get("patch_target") or f"{command_fn.__module__}.{command_fn.__qualname__.split('.')[-1]}"
    with patch(patch_target, new_callable=AsyncMock) as mock_command:
        with ExitStack() as stack:
            stack.enter_context(extension_patches(extension, (), ()))
            interaction = await invoke_interaction_command(
                handler,
                owner=group,
                extra_kwargs=extra,
                bot=bot,
            )
        interaction.response.defer.assert_awaited()
        mock_command.assert_awaited_once()

from __future__ import annotations

import importlib
import inspect
import json
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord.ext import commands

from diagnostics.discovery import _instantiate_group
from diagnostics.harness import invoke_interaction_command
from tests.helpers.command_matrix.dimensions import kwargs_for_matrix_case
from tests.helpers.command_matrix.harness import permission_for_case
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.patches import matrix_patches
from tests.helpers.command_matrix.resolver import _import_alias_map, resolve_command_callable
from tests.helpers.discord import make_guild, make_member, make_permissions, make_text_channel
from tests.helpers.permission_profiles import command_info_for_permission

ROOT = Path(__file__).resolve().parents[3]
_HANDLERS_JSON = ROOT / "coverage" / "command_handlers.json"

UI_DEFERRED_PATHS: frozenset[str] = frozenset(
    {
        "admin_emoji_name admin_createemoji_name",
    }
)

UI_ONLY_PATHS: frozenset[str] = frozenset(
    {
        "setup_name setup_booster_name",
    }
)

INLINE_REPLY_PATHS: frozenset[str] = frozenset(
    {
        "utilitycmd_name utility_boosterchannel_name utility_boosterchannelinfo_name",
        "utilitycmd_name utility_boosterrole_name utility_boosterroleinfo_name",
    }
)


def _load_path_meta(tree_path: str) -> dict[str, str] | None:
    if not _HANDLERS_JSON.is_file():
        return None
    data = json.loads(_HANDLERS_JSON.read_text(encoding="utf-8"))
    return (data.get("path_meta") or {}).get(tree_path)


def _instantiate_group_for_case(group_cls: type, bot: MagicMock) -> object:
    if issubclass(group_cls, commands.Cog):
        return group_cls(bot)
    params = inspect.signature(group_cls.__init__).parameters
    if "bot" in params:
        return group_cls(bot)
    group = _instantiate_group(group_cls)
    if group is None:
        pytest.fail(f"Could not instantiate group {group_cls.__qualname__}")
    return group


def _assert_interaction_responded(interaction: MagicMock, case: MatrixCase) -> None:
    if interaction.response.send_modal.await_count > 0:
        return
    if interaction.response.defer.await_count > 0:
        return
    if interaction.response.send_message.await_count > 0:
        return
    if interaction.followup.send.await_count > 0:
        return
    if interaction.edit_original_response.await_count > 0:
        return
    pytest.fail(f"No interaction response for {case.id}")


def _profile_context(case: MatrixCase) -> tuple[MagicMock | None, MagicMock | None, MagicMock | None]:
    profile = case.dimension("permission")
    if not profile and case.group == "setup_name":
        profile = "admin"
    if not profile:
        return None, None, None
    info = command_info_for_permission(profile)
    user = info.user
    guild = info.guild
    channel = info.channel
    if channel is not None and user is not None:
        perms = getattr(user, "guild_permissions", make_permissions())
        channel.permissions_for = MagicMock(return_value=perms)
    return user, guild, channel


PATCH_TARGET_OVERRIDES: dict[str, str] = {
    "ai_name ai_askcustom_name": "services.ai_service.AiService.get_situation",
    "setup_name setup_giveaway_name": "commands.giveaway.start.start_giveaway",
}


def _resolve_patch_target(meta: dict[str, str], command_fn: object, extension: str, tree_path: str) -> str:
    patch_target = meta.get("patch_target") or (
        f"{command_fn.__module__}.{command_fn.__qualname__.split('.')[-1]}"
    )
    if ".command_info" in patch_target:
        return f"{command_fn.__module__}.{command_fn.__qualname__.split('.')[-1]}"
    override = PATCH_TARGET_OVERRIDES.get(tree_path)
    if override:
        return override
    prefix = f"{extension}."
    if not patch_target.startswith(prefix):
        return patch_target
    alias = patch_target[len(prefix) :]
    imports = _import_alias_map(extension)
    if "." in alias:
        base, method = alias.split(".", 1)
        imported = imports.get(base)
        if imported:
            return f"{imported}.{method}"
    elif alias in imports:
        return f"{extension}.{alias}"
    return patch_target


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
    group = _instantiate_group_for_case(group_cls, bot)
    handler = getattr(group, method_name, None)
    if handler is None:
        pytest.fail(f"Handler {method_name!r} missing for {case.id}")

    extra = kwargs_for_matrix_case(case)
    profile_user, profile_guild, profile_channel = _profile_context(case)
    if profile_user is not None:
        extra["user"] = profile_user

    patch_target = _resolve_patch_target(meta, command_fn, extension, case.tree_path)
    handler_alias = patch_target.rsplit(".", 1)[-1]
    ui_deferred = case.tree_path in UI_DEFERRED_PATHS
    inline_reply = case.tree_path in INLINE_REPLY_PATHS
    ui_only = case.tree_path in UI_ONLY_PATHS

    with ExitStack() as stack:
        stack.enter_context(matrix_patches(case))
        mock_command = None
        if not ui_only and not inline_reply:
            stack.enter_context(extension_patches(extension, (), (handler_alias,)))
            mock_command = stack.enter_context(patch(patch_target, new_callable=AsyncMock))
        else:
            stack.enter_context(extension_patches(extension, (), ()))
        interaction = await invoke_interaction_command(
            handler,
            owner=group,
            user=profile_user,
            guild=profile_guild,
            channel=profile_channel,
            extra_kwargs=extra,
            bot=bot,
        )

    if ui_deferred or ui_only:
        responded = (
            interaction.response.send_message.await_count > 0
            or interaction.followup.send.await_count > 0
        )
        assert responded, f"Expected UI response for {case.id}"
    elif inline_reply:
        _assert_interaction_responded(interaction, case)
    else:
        mock_command.assert_awaited_once()

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models import LogEnableModel
from tests.helpers.discord import (
    make_app_command_channel,
    make_guild,
    make_interaction,
    make_member,
    make_permissions,
    make_text_channel,
)

GUILD_ID = "123456789012345678"


def log_enable_model(**flags: bool) -> LogEnableModel:
    defaults = {k: True for k in LogEnableModel._OPTION_KEYS}
    defaults.update(flags)
    return LogEnableModel(guild_id=GUILD_ID, **defaults)


def admin_interaction(*, guild: MagicMock | None = None) -> MagicMock:
    guild = guild or make_guild()
    channel = make_text_channel(guild=guild)
    user = make_member(guild_permissions=make_permissions(administrator=True))
    ix = make_interaction(user=user, guild=guild, channel=channel)
    ix.client = MagicMock()
    ix.client.user = MagicMock(id=999999999)
    ix.response.edit_message = AsyncMock()
    ix.response.send_message = AsyncMock()
    ix.response.send_modal = AsyncMock()
    channel.permissions_for = MagicMock(
        side_effect=lambda _m: make_permissions(
            administrator=True, send_messages=True, view_channel=True
        )
    )
    guild.get_member = MagicMock(return_value=user)
    return ix


def non_admin_interaction() -> MagicMock:
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    user = make_member(guild_permissions=make_permissions(administrator=False))
    ix = make_interaction(user=user, guild=guild, channel=channel)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=False))
    ix.response.send_message = AsyncMock()
    ix.response.edit_message = AsyncMock()
    return ix


def resolved_app_command_channel(
    guild: MagicMock,
    *,
    send_messages: bool = True,
    view_channel: bool = True,
) -> MagicMock:
    resolved = make_text_channel(guild=guild)
    resolved.permissions_for = MagicMock(
        return_value=make_permissions(send_messages=send_messages, view_channel=view_channel)
    )
    return make_app_command_channel(guild=guild, resolved=resolved)


def identity_ui(**kwargs):
    def decorator(func):
        return func

    return decorator


@pytest.fixture
def wizard_api_mocks():
    import extensions.setup_wizards as sw_mod

    with (
        patch.object(sw_mod, "api_set_log_channel", new=AsyncMock()) as set_log,
        patch.object(sw_mod, "api_set_log_enable", new=AsyncMock()) as set_enable,
        patch.object(sw_mod, "api_get_log_enable", new=AsyncMock(return_value=log_enable_model())),
        patch.object(sw_mod, "api_get_log_channel", new=AsyncMock(return_value=None)),
        patch.object(sw_mod, "api_set_level_system_status", new=AsyncMock()) as set_level,
        patch.object(sw_mod, "api_set_levelup_channel", new=AsyncMock()),
        patch.object(sw_mod, "api_set_text_cooldown", new=AsyncMock()),
        patch.object(sw_mod, "api_set_voice_cooldown", new=AsyncMock()),
        patch.object(sw_mod, "api_set_xp_scaling", new=AsyncMock()),
        patch.object(sw_mod, "api_get_level_system_status", new=AsyncMock(return_value=False)),
    ):
        yield {"set_log": set_log, "set_enable": set_enable, "set_level": set_level}


@pytest.fixture
def setup_wizards_module():
    import importlib

    import extensions.setup_wizards as sw_mod

    with patch("discord.ui.select", identity_ui), patch("discord.ui.button", identity_ui):
        importlib.reload(sw_mod)
        yield sw_mod
        importlib.reload(sw_mod)

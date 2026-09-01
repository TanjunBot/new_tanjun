from __future__ import annotations

import sys
from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from tests.helpers.db import make_bot, make_mock_pool
from tests.helpers.discord import (
    _ensure_discord_types,
    make_command_info,
    make_guild,
    make_member,
    make_permissions,
    make_text_channel,
)
from tests.helpers.discord import (
    make_role as _make_role,
)

_ensure_discord_types()

import discord

discord.NotFound = type("NotFound", (Exception,), {})
if not hasattr(discord, "utils") or discord.utils is None:
    discord.utils = MagicMock()
sys.modules["discord.ui"] = discord.ui
discord.ButtonStyle = MagicMock()
discord.ButtonStyle.primary = "primary"
discord.ButtonStyle.secondary = "secondary"
discord.ButtonStyle.success = "success"
discord.ButtonStyle.danger = "danger"
discord.ButtonStyle.green = "green"
discord.ButtonStyle.red = "red"
discord.ButtonStyle.gray = "gray"
discord.TextStyle = MagicMock()
discord.TextStyle.short = "short"
discord.TextStyle.paragraph = "paragraph"
if hasattr(discord.app_commands, "autocomplete"):
    discord.app_commands.autocomplete = lambda *a, **k: lambda f: f
discord.ui.UserSelect = MagicMock()
discord.ui.ChannelSelect = MagicMock()
discord.ui.RoleSelect = MagicMock()
discord.ChannelType = MagicMock()
discord.ChannelType.text = "text"
discord.ChannelType.voice = "voice"
discord.CategoryChannel = type("CategoryChannel", (), {})
discord.ForumChannel = type("ForumChannel", (), {})
discord.StageChannel = type("StageChannel", (), {})
discord.DMChannel = type("DMChannel", (), {})
discord.errors = MagicMock()
discord.errors.NotFound = discord.NotFound
discord.PermissionOverwrite = MagicMock()
discord.File = MagicMock()
discord.SelectOption = MagicMock()
discord.SelectDefaultValue = MagicMock()
discord.SelectDefaultValueType = MagicMock()
discord.SelectDefaultValueType.role = "role"
discord.SelectDefaultValueType.user = "user"


@pytest.fixture(autouse=True)
def api_bot() -> Iterator[None]:
    pool, _, _ = make_mock_pool()
    make_bot(pool)
    yield
    from api import set_bot

    set_bot(None)


@pytest.fixture
def reply() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def full_permissions() -> MagicMock:
    return make_permissions(
        administrator=True,
        ban_members=True,
        kick_members=True,
        manage_roles=True,
        manage_messages=True,
        manage_guild=True,
        manage_channels=True,
        moderate_members=True,
        send_messages=True,
    )


@pytest.fixture
def no_permissions() -> MagicMock:
    return make_permissions(
        administrator=False,
        ban_members=False,
        kick_members=False,
        manage_roles=False,
        manage_messages=False,
        manage_guild=False,
        manage_channels=False,
        moderate_members=False,
        send_messages=False,
    )


@pytest.fixture
def no_guild_command_info(no_permissions: MagicMock, reply: AsyncMock) -> MagicMock:
    user = make_member(top_role_position=1)
    user.guild_permissions = no_permissions
    channel = make_text_channel()
    channel.guild = None
    channel.permissions_for = MagicMock(return_value=no_permissions)
    info = make_command_info(user=user, channel=channel, reply=reply)
    info.guild = None
    return info


@pytest.fixture
def admin_command_info(full_permissions: MagicMock, reply: AsyncMock) -> MagicMock:
    user = make_member(top_role_position=50)
    user.guild_permissions = full_permissions
    guild = make_guild(me_permissions=full_permissions, me_top_role_position=100)
    guild.get_member = MagicMock(side_effect=lambda uid: guild.me if uid == guild.me.id else None)
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=full_permissions)
    client = MagicMock()
    client.user = MagicMock(id=guild.me.id)
    return make_command_info(user=user, guild=guild, channel=channel, reply=reply, client=client)


@pytest.fixture
def restricted_command_info(no_permissions: MagicMock, reply: AsyncMock) -> MagicMock:
    user = make_member(top_role_position=1)
    user.guild_permissions = no_permissions
    guild = make_guild(me_permissions=no_permissions)
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=no_permissions)
    return make_command_info(user=user, guild=guild, channel=channel, reply=reply)


@pytest.fixture
def admin_info(admin_command_info: MagicMock) -> MagicMock:
    return admin_command_info


@pytest.fixture
def member_info(restricted_command_info: MagicMock) -> MagicMock:
    return restricted_command_info


def embed_from_reply(reply: AsyncMock) -> MagicMock:
    reply.assert_awaited()
    call = reply.await_args
    assert call is not None
    embed = call.kwargs.get("embed")
    assert embed is not None
    return embed


def make_user(user_id: int = 333333333) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    return user


def make_role(role_id: int = 222222222, **kwargs):
    return _make_role(role_id=role_id, **kwargs)

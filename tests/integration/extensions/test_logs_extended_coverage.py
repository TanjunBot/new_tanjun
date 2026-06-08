from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_guild, make_member, make_role
from tests.helpers.extensions import async_audit_logs, make_log_enable
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.logs"


@pytest.fixture
def log_mocks():
    with (
        patch("extensions.logs.get_log_enable", new=AsyncMock(return_value=make_log_enable())),
        patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=None)),
        patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=[])),
        patch("extensions.logs.get_log_channel", new=AsyncMock(return_value="444444444")),
        patch("extensions.logs.log_event_producer", new=AsyncMock()) as producer,
    ):
        yield producer


def _role_pair(guild):
    before = make_role()
    after = make_role()
    before.guild = guild
    after.guild = guild
    shared_color = MagicMock()
    before.color = shared_color
    after.color = shared_color
    before.hoist = after.hoist = False
    before.mentionable = after.mentionable = False
    before.managed = after.managed = False
    before.display_icon = after.display_icon = None
    before.icon = after.icon = None
    before.name = after.name = "Role"
    return before, after


async def test_guild_update_emoji_additions(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    before = make_guild()
    after = make_guild()
    emoji = MagicMock()
    emoji.name = "newemoji"
    emoji.__str__ = lambda self: ":newemoji:"
    before.emojis = []
    after.emojis = [emoji]
    before.emoji_limit = 50
    after.emoji_limit = 100
    await cog.on_guild_update(before, after)
    log_mocks.assert_awaited()


async def test_guild_update_emoji_removals(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    emoji = MagicMock()
    emoji.name = "gone"
    emoji.__str__ = lambda self: ":gone:"
    before = make_guild()
    after = make_guild()
    before.emojis = [emoji]
    after.emojis = []
    await cog.on_guild_update(before, after)
    log_mocks.assert_awaited()


async def test_guild_update_features_added_removed(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    before = make_guild()
    after = make_guild()
    before.features = ["COMMUNITY"]
    after.features = ["COMMUNITY", "NEWS"]
    before.name = "Old"
    after.name = "New"
    await cog.on_guild_update(before, after)
    log_mocks.assert_awaited()


async def test_guild_role_update_removed_permissions(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before, after = _role_pair(guild)
    before.name = "OldRole"
    after.name = "NewRole"
    before.permissions = [("send_messages", True), ("ban_members", True)]
    after.permissions = [("send_messages", True)]
    await cog.on_guild_role_update(before, after)
    log_mocks.assert_awaited()


async def test_guild_role_update_display_icon_change(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before, after = _role_pair(guild)
    before.permissions = after.permissions = []
    before.hoist = False
    after.hoist = True
    icon = MagicMock()
    icon.url = "https://cdn.discordapp.com/icon.png"
    after.display_icon = icon
    await cog.on_guild_role_update(before, after)
    log_mocks.assert_awaited()


async def test_guild_role_update_icon_change(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before, after = _role_pair(guild)
    before.permissions = after.permissions = []
    before.mentionable = False
    after.mentionable = True
    before.icon = "old_icon"
    after.icon = "new_icon"
    await cog.on_guild_role_update(before, after)
    log_mocks.assert_awaited()


async def test_guild_role_update_single_change_skips(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before, after = _role_pair(guild)
    before.permissions = after.permissions = []
    before.name = "Before"
    after.name = "After"
    await cog.on_guild_role_update(before, after)
    log_mocks.assert_not_awaited()


async def test_member_update_display_name_change(log_mocks) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    before = make_member()
    after = make_member()
    before.guild = guild
    after.guild = guild
    before.display_name = "old"
    after.display_name = "new"
    before.display_avatar = after.display_avatar
    before.banner = after.banner
    before.roles = after.roles = []
    before.pending = after.pending = False
    before.timed_out_until = after.timed_out_until = None
    await cog.on_member_update(before, after)
    log_mocks.assert_awaited_once()

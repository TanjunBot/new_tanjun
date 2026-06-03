from __future__ import annotations

from unittest.mock import AsyncMock

import discord
import pytest

from tests.helpers.discord import (
    make_app_command_channel,
    make_guild,
    make_member,
    make_permissions,
    make_text_channel,
)
from utils.discord_channels import (
    bot_can_send_messages,
    channel_mention,
    resolve_guild_channel,
    resolve_guild_channel_sync,
)


@pytest.mark.asyncio
async def test_resolve_guild_channel_passthrough_guild_channel() -> None:
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    result = await resolve_guild_channel(guild, channel)
    assert result is channel


@pytest.mark.asyncio
async def test_resolve_guild_channel_from_app_command_resolve() -> None:
    guild = make_guild()
    resolved = make_text_channel(guild=guild)
    selected = make_app_command_channel(guild=guild, resolved=resolved)
    result = await resolve_guild_channel(guild, selected)
    assert result is resolved
    selected.fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_guild_channel_from_app_command_fetch() -> None:
    guild = make_guild()
    resolved = make_text_channel(guild=guild)
    selected = make_app_command_channel(guild=guild, resolved=None)
    selected.fetch = AsyncMock(return_value=resolved)
    result = await resolve_guild_channel(guild, selected)
    assert result is resolved
    selected.fetch.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("exc", [discord.NotFound, discord.Forbidden])
async def test_resolve_guild_channel_fetch_failure(exc: type[BaseException]) -> None:
    guild = make_guild()
    selected = make_app_command_channel(guild=guild, resolved=None, fetch_raises=exc)
    result = await resolve_guild_channel(guild, selected)
    assert result is None


@pytest.mark.asyncio
async def test_resolve_guild_channel_wrong_guild() -> None:
    guild = make_guild()
    selected = make_app_command_channel(guild=make_guild(guild_id=999))
    result = await resolve_guild_channel(guild, selected)
    assert result is None
    selected.resolve.assert_not_called()


def test_resolve_guild_channel_sync() -> None:
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    assert resolve_guild_channel_sync(guild, channel) is channel


def test_bot_can_send_messages() -> None:
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    bot = make_member()
    from unittest.mock import MagicMock

    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    assert bot_can_send_messages(channel, bot) is True
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    assert bot_can_send_messages(channel, bot) is False


def test_channel_mention() -> None:
    guild = make_guild()
    channel = make_text_channel(channel_id=123, guild=guild)
    assert channel_mention(channel) == '<#123>'
    selected = make_app_command_channel(channel_id=456, guild=guild)
    assert channel_mention(selected) == '<#456>'
    assert channel_mention(selected, channel) == '<#123>'

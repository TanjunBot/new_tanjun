from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

import utils.discord_channels as dc


class _AccChannel:
    mention = '<#acc>'


class _AccThread:
    mention = '<#thread>'


def test_is_partial_channel_app_command_types() -> None:
    with (
        patch.object(dc, '_app_command_channel_type', return_value=_AccChannel),
        patch.object(dc, '_app_command_thread_type', return_value=_AccThread),
    ):
        assert dc._is_partial_channel(_AccChannel()) is True
        assert dc._is_partial_channel(_AccThread()) is True


def test_is_partial_channel_generic_partial() -> None:
    selected = MagicMock(
        resolve=MagicMock(),
        fetch=AsyncMock(),
        guild_id=1,
        spec=['resolve', 'fetch', 'guild_id'],
    )
    assert dc._is_partial_channel(selected) is True


@pytest.mark.asyncio
async def test_resolve_guild_channel_guild_channel() -> None:
    guild = MagicMock(id=1)
    channel = MagicMock(spec=discord.abc.GuildChannel)
    assert await dc.resolve_guild_channel(guild, channel) is channel


@pytest.mark.asyncio
async def test_resolve_guild_channel_unsupported() -> None:
    guild = MagicMock(id=1)
    assert await dc.resolve_guild_channel(guild, MagicMock()) is None


@pytest.mark.asyncio
async def test_resolve_guild_channel_partial_fetch() -> None:
    guild = MagicMock(id=1)
    resolved = MagicMock()
    selected = MagicMock(guild_id=1, resolve=MagicMock(return_value=None))
    selected.fetch = AsyncMock(return_value=resolved)
    with patch.object(dc, '_is_partial_channel', return_value=True):
        assert await dc.resolve_guild_channel(guild, selected) is resolved


@pytest.mark.asyncio
async def test_resolve_guild_channel_partial_wrong_guild() -> None:
    guild = MagicMock(id=1)
    selected = MagicMock(guild_id=2, resolve=MagicMock(return_value=None))
    with patch.object(dc, '_is_partial_channel', return_value=True):
        assert await dc.resolve_guild_channel(guild, selected) is None


def test_resolve_guild_channel_sync_paths() -> None:
    guild = MagicMock(id=1)
    channel = MagicMock(spec=discord.abc.GuildChannel)
    assert dc.resolve_guild_channel_sync(guild, channel) is channel

    selected = MagicMock(guild_id=2, resolve=MagicMock())
    with patch.object(dc, '_is_partial_channel', return_value=True):
        assert dc.resolve_guild_channel_sync(guild, selected) is None

    resolved = MagicMock()
    selected_ok = MagicMock(guild_id=1, resolve=MagicMock(return_value=resolved))
    with patch.object(dc, '_is_partial_channel', return_value=True):
        assert dc.resolve_guild_channel_sync(guild, selected_ok) is resolved


def test_channel_mention_paths() -> None:
    resolved = MagicMock(mention='<#resolved>')
    assert dc.channel_mention(MagicMock(), resolved=resolved) == '<#resolved>'

    with patch.object(dc, '_app_command_channel_type', return_value=_AccChannel):
        assert dc.channel_mention(_AccChannel()) == '<#acc>'

    with patch.object(dc, '_app_command_thread_type', return_value=_AccThread):
        assert dc.channel_mention(_AccThread()) == '<#thread>'

    fallback = MagicMock(mention='<#fallback>')
    assert dc.channel_mention(fallback) == '<#fallback>'


def test_bot_can_send_messages() -> None:
    channel = MagicMock()
    channel.permissions_for = MagicMock(return_value=MagicMock(send_messages=True))
    bot = MagicMock()
    assert dc.bot_can_send_messages(channel, bot) is True

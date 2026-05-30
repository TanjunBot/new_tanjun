"""Integration tests for commands.logs.blacklist_channel.blacklist_channel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.logs.blacklist_channel.blacklist_channel import blacklist_channel as command_fn
from tests.helpers.discord import make_command_info, make_guild, make_permissions, make_text_channel
from tests.integration.commands.conftest import embed_from_reply


def _admin_info():
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=True))
    return make_command_info(guild=guild, channel=channel)


def _no_admin_info():
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=False))
    return make_command_info(guild=guild, channel=channel)


@pytest.mark.asyncio
async def test_missing_permission():
    info = _no_admin_info()
    await command_fn(info, make_text_channel())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.logs.blacklist_channel.blacklist_channel.is_log_entity_blacklisted", new_callable=AsyncMock)
@patch("commands.logs.blacklist_channel.blacklist_channel.add_log_blacklist", new_callable=AsyncMock)
async def test_success(mock_add, mock_is):
    mock_is.return_value = False
    info = _admin_info()
    await command_fn(info, make_text_channel())
    embed_from_reply(info.reply)
    mock_add.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.logs.blacklist_channel.blacklist_channel.is_log_entity_blacklisted", new_callable=AsyncMock)
async def test_already_blacklisted(mock_is):
    mock_is.return_value = True
    info = _admin_info()
    await command_fn(info, make_text_channel())
    embed_from_reply(info.reply)

"""Integration tests for commands.logs.set_log_channel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.logs.set_log_channel import set_log_channel as command_fn


def _info(admin: bool):
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=admin))
    bot_member = MagicMock()
    guild.get_member = MagicMock(return_value=bot_member)
    client = MagicMock()
    client.user = MagicMock(id=999)
    return make_command_info(guild=guild, channel=channel, client=client)


@pytest.mark.asyncio
async def test_missing_permission():
    info = _info(False)
    await command_fn(info, make_text_channel())
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.logs.set_log_channel.get_log_channel_api", new_callable=AsyncMock)
async def test_already_set(mock_get):
    import commands.logs.set_log_channel as mod

    mock_get.return_value = 1
    info = _info(True)
    ch = make_text_channel(guild=info.guild)
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    bot_member = MagicMock()
    info.guild.get_member = MagicMock(return_value=bot_member)
    mod.CommandInfo.guild = info.guild
    try:
        await command_fn(info, ch)
        embed_from_reply(info.reply)
    finally:
        if hasattr(mod.CommandInfo, "guild"):
            del mod.CommandInfo.guild


@pytest.mark.asyncio
@patch("commands.logs.set_log_channel.set_log_channel_api", new_callable=AsyncMock)
@patch("commands.logs.set_log_channel.get_log_channel_api", new_callable=AsyncMock)
async def test_success(mock_get, mock_set):
    import commands.logs.set_log_channel as mod

    mock_get.return_value = None
    info = _info(True)
    ch = make_text_channel(guild=info.guild)
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    bot_member = MagicMock()
    info.guild.get_member = MagicMock(return_value=bot_member)
    mod.CommandInfo.guild = info.guild
    try:
        await command_fn(info, ch)
        embed_from_reply(info.reply)
        mock_set.assert_awaited_once()
    finally:
        if hasattr(mod.CommandInfo, "guild"):
            del mod.CommandInfo.guild

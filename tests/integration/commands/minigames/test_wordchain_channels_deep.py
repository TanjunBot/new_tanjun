from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.minigames.wordchain.removewordchainchannel import removewordchainchannel
from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_remove_wordchain_no_guild(admin_command_info):
    admin_command_info.guild = None
    await removewordchainchannel(admin_command_info, make_text_channel())


async def test_remove_wordchain_not_configured(admin_command_info):
    with patch(
        "commands.minigames.wordchain.removewordchainchannel.get_wordchain_word",
        new_callable=AsyncMock,
        return_value=None,
    ):
        await removewordchainchannel(admin_command_info, make_text_channel(guild=admin_command_info.guild))
    admin_command_info.reply.assert_awaited_once()


@patch("commands.minigames.wordchain.removewordchainchannel.clear_wordchain", new_callable=AsyncMock)
@patch("commands.minigames.wordchain.removewordchainchannel.get_wordchain_word", new_callable=AsyncMock, return_value="hi")
async def test_remove_wordchain_success(mock_get, mock_clear, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.send = AsyncMock()
    await removewordchainchannel(admin_command_info, ch)
    mock_clear.assert_awaited_once()
    ch.send.assert_awaited_once()


async def test_set_wordchain_missing_manage_messages(admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_member = MagicMock()
    perms = make_permissions(send_messages=True, manage_messages=False, read_messages=True, view_channel=True)
    ch.permissions_for = MagicMock(return_value=perms)
    admin_command_info.guild.get_member = MagicMock(return_value=bot_member)
    await setwordchainchannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


async def test_set_wordchain_missing_read_messages(admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_member = MagicMock()
    perms = make_permissions(send_messages=True, manage_messages=True, read_messages=False, view_channel=True)
    ch.permissions_for = MagicMock(return_value=perms)
    admin_command_info.guild.get_member = MagicMock(return_value=bot_member)
    await setwordchainchannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()

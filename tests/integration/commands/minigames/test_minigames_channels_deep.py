from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.minigames.counting.setcountingchannel import setCountingChannel
from commands.minigames.counting_challenge.setcountingchannel import setCountingChannel as setChallengeChannel
from commands.minigames.counting_modes.setcountingchannel import setCountingChannel as setModesChannel
from commands.minigames.wordchain.removewordchainchannel import removewordchainchannel
from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_set_counting_channel_no_guild(admin_command_info):
    admin_command_info.guild = None
    ch = make_text_channel()
    await setCountingChannel(admin_command_info, ch)


@patch("commands.minigames.counting.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=True)
@patch("commands.minigames.counting.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_counting_channel_bot_perms_fail(mock_mod, mock_bot, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    await setCountingChannel(admin_command_info, ch)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting.setcountingchannel.CountingRepository.set_progress", new_callable=AsyncMock)
@patch("commands.minigames.counting.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=False)
@patch("commands.minigames.counting.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_counting_channel_success(mock_mod, mock_bot, mock_set, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.send = AsyncMock()
    await setCountingChannel(admin_command_info, ch)
    ch.send.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_set_challenge_channel_no_guild(admin_command_info):
    admin_command_info.guild = None
    await setChallengeChannel(admin_command_info, make_text_channel())


@patch("commands.minigames.counting_challenge.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=True)
@patch("commands.minigames.counting_challenge.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_challenge_channel_bot_perms_fail(mock_mod, mock_bot, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    await setChallengeChannel(admin_command_info, ch)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting_challenge.setcountingchannel.CountingRepository.set_challenge_progress", new_callable=AsyncMock)
@patch("commands.minigames.counting_challenge.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=False)
@patch("commands.minigames.counting_challenge.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_challenge_channel_success(mock_mod, mock_bot, mock_set, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.send = AsyncMock()
    await setChallengeChannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


async def test_set_modes_channel_no_guild(admin_command_info):
    admin_command_info.guild = None
    await setModesChannel(admin_command_info, make_text_channel())


@patch("commands.minigames.counting_modes.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=True)
@patch("commands.minigames.counting_modes.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_modes_channel_bot_perms_fail(mock_mod, mock_bot, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    await setModesChannel(admin_command_info, ch)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting_modes.setcountingchannel.CountingRepository.set_mode_progress", new_callable=AsyncMock)
@patch("commands.minigames.counting_modes.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=False)
@patch("commands.minigames.counting_modes.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_modes_channel_success(mock_mod, mock_bot, mock_set, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.send = AsyncMock()
    await setModesChannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


async def test_set_wordchain_no_guild(admin_command_info):
    admin_command_info.guild = None
    await setwordchainchannel(admin_command_info, make_text_channel())


async def test_set_wordchain_no_moderate(admin_command_info):
    perms = make_permissions(moderate_members=False)
    admin_command_info.channel.permissions_for = MagicMock(return_value=perms)
    await setwordchainchannel(admin_command_info, make_text_channel(guild=admin_command_info.guild))
    admin_command_info.reply.assert_awaited_once()


async def test_set_wordchain_no_client_user(admin_command_info):
    admin_command_info.client.user = None
    await setwordchainchannel(admin_command_info, make_text_channel(guild=admin_command_info.guild))


async def test_set_wordchain_no_self_member(admin_command_info):
    admin_command_info.guild.get_member = MagicMock(return_value=None)
    await setwordchainchannel(admin_command_info, make_text_channel(guild=admin_command_info.guild))


async def test_set_wordchain_missing_send_perms(admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_member = MagicMock()
    bot_perms = make_permissions(send_messages=False)
    ch.permissions_for = MagicMock(return_value=bot_perms)
    admin_command_info.guild.get_member = MagicMock(return_value=bot_member)
    await setwordchainchannel(admin_command_info, ch)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.minigames.wordchain.setwordchainchannel.set_wordchain_word", new_callable=AsyncMock)
async def test_set_wordchain_success(mock_set, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    bot_member = MagicMock()
    full = make_permissions(
        send_messages=True,
        manage_messages=True,
        read_messages=True,
        view_channel=True,
    )
    ch.permissions_for = MagicMock(return_value=full)
    admin_command_info.guild.get_member = MagicMock(return_value=bot_member)
    ch.send = AsyncMock()
    await setwordchainchannel(admin_command_info, ch)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_remove_wordchain_no_guild(admin_command_info):
    admin_command_info.guild = None
    await removewordchainchannel(admin_command_info, make_text_channel())

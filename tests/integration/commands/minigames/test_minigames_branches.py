import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.minigames.counting.removecountingchannel import removeCountingChannel
from commands.minigames.counting.setcountingchannel import setCountingChannel
from commands.minigames.counting.setcountingprogress import setCountingProgress
from commands.minigames.wordchain.removewordchainchannel import removewordchainchannel
from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


def _setup_bot_member(info):
    info.client.user = MagicMock(id=info.guild.me.id)
    info.guild.get_member = MagicMock(return_value=info.guild.me)


@patch("commands.minigames.counting.setcountingchannel._repo")
@patch("commands.minigames.counting.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=False)
@patch("commands.minigames.counting.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_counting_channel_success(mock_mod, mock_bot, mock_repo, admin_command_info):
    _setup_bot_member(admin_command_info)
    mock_repo.set_progress = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.send = AsyncMock()
    await setCountingChannel(admin_command_info, channel)
    mock_repo.set_progress.assert_awaited_once()


async def test_set_counting_channel_no_permission(restricted_command_info):
    with patch("commands.minigames.counting.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=True):
        channel = make_text_channel(guild=restricted_command_info.guild)
        await setCountingChannel(restricted_command_info, channel)


@patch("commands.minigames.counting.removecountingchannel._repo")
@patch("commands.minigames.counting.removecountingchannel.require_counting_channel", new_callable=AsyncMock, return_value=5)
@patch("commands.minigames.counting.removecountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_remove_counting_channel_success(mock_mod, mock_req, mock_repo, admin_command_info):
    mock_repo.clear = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    await removeCountingChannel(admin_command_info, channel)
    mock_repo.clear.assert_awaited_once()


@patch("commands.minigames.counting.setcountingprogress._repo")
@patch("commands.minigames.counting.setcountingprogress.require_valid_progress", new_callable=AsyncMock, return_value=False)
@patch("commands.minigames.counting.setcountingprogress.require_counting_channel", new_callable=AsyncMock, return_value=0)
@patch("commands.minigames.counting.setcountingprogress.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_set_counting_progress_success(mock_mod, mock_req, mock_valid, mock_repo, admin_command_info):
    mock_repo.set_progress = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    await setCountingProgress(admin_command_info, channel, 42)
    mock_repo.set_progress.assert_awaited_once()


async def test_set_counting_progress_no_permission(restricted_command_info):
    with patch("commands.minigames.counting.setcountingprogress.require_moderate_members", new_callable=AsyncMock, return_value=True):
        channel = make_text_channel(guild=restricted_command_info.guild)
        await setCountingProgress(restricted_command_info, channel, 1)


@patch("commands.minigames.wordchain.setwordchainchannel.set_wordchain_word", new_callable=AsyncMock)
async def test_set_wordchain_channel_success(mock_set, admin_command_info):
    _setup_bot_member(admin_command_info)
    channel = make_text_channel(guild=admin_command_info.guild)
    await setwordchainchannel(admin_command_info, channel)
    mock_set.assert_awaited_once()


async def test_set_wordchain_no_send_permission(admin_command_info):
    _setup_bot_member(admin_command_info)
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    await setwordchainchannel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


async def test_set_wordchain_no_manage_messages(admin_command_info):
    _setup_bot_member(admin_command_info)
    channel = make_text_channel(guild=admin_command_info.guild)

    def perms_for(member):
        p = make_permissions(send_messages=True, manage_messages=False, read_messages=True, view_channel=True)
        return p

    channel.permissions_for = MagicMock(side_effect=perms_for)
    await setwordchainchannel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.minigames.wordchain.removewordchainchannel.clear_wordchain", new_callable=AsyncMock)
@patch("commands.minigames.wordchain.removewordchainchannel.get_wordchain_word", new_callable=AsyncMock, return_value="hello")
async def test_remove_wordchain_channel_success(mock_get, mock_clear, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await removewordchainchannel(admin_command_info, channel)
    mock_clear.assert_awaited_once()


async def test_remove_wordchain_no_permission(restricted_command_info):
    channel = make_text_channel(guild=restricted_command_info.guild)
    await removewordchainchannel(restricted_command_info, channel)
    restricted_command_info.reply.assert_awaited_once()

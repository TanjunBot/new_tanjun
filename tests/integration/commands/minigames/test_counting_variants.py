from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.minigames.counting_challenge.removecountingchannel import removecountingchallengechannel
from commands.minigames.counting_challenge.setcountingchannel import setCountingChannel as setChallenge
from commands.minigames.counting_modes.removecountingchannel import removecountingmodeschannel
from commands.minigames.counting_modes.setcountingchannel import setCountingChannel as setModes
from tests.helpers.discord import make_text_channel

pytestmark = pytest.mark.asyncio


def _setup_bot_member(info):
    info.client.user = MagicMock(id=info.guild.me.id)
    info.guild.get_member = MagicMock(return_value=info.guild.me)


@patch("commands.minigames.counting_challenge.setcountingchannel._repo")
@patch(
    "commands.minigames.counting_challenge.setcountingchannel.require_bot_permissions",
    new_callable=AsyncMock,
    return_value=False,
)
@patch(
    "commands.minigames.counting_challenge.setcountingchannel.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_set_challenge_counting_channel(mock_mod, mock_bot, mock_repo, admin_command_info):
    _setup_bot_member(admin_command_info)
    mock_repo.set_challenge_progress = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.send = AsyncMock()
    await setChallenge(admin_command_info, channel)
    mock_repo.set_challenge_progress.assert_awaited_once()


@patch("commands.minigames.counting_challenge.removecountingchannel._repo")
@patch(
    "commands.minigames.counting_challenge.removecountingchannel.require_counting_channel",
    new_callable=AsyncMock,
    return_value=3,
)
@patch(
    "commands.minigames.counting_challenge.removecountingchannel.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_remove_challenge_counting_channel(mock_mod, mock_req, mock_repo, admin_command_info):
    mock_repo.clear = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    await removecountingchallengechannel(admin_command_info, channel)
    mock_repo.clear.assert_awaited_once()


@patch("commands.minigames.counting_modes.setcountingchannel._repo")
@patch(
    "commands.minigames.counting_modes.setcountingchannel.require_bot_permissions", new_callable=AsyncMock, return_value=False
)
@patch(
    "commands.minigames.counting_modes.setcountingchannel.require_moderate_members", new_callable=AsyncMock, return_value=False
)
async def test_set_modes_counting_channel(mock_mod, mock_bot, mock_repo, admin_command_info):
    _setup_bot_member(admin_command_info)
    mock_repo.set_mode_progress = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.send = AsyncMock()
    await setModes(admin_command_info, channel)
    mock_repo.set_mode_progress.assert_awaited_once()


@patch(
    "commands.minigames.counting_challenge.removecountingchannel.require_moderate_members",
    new_callable=AsyncMock,
    return_value=True,
)
async def test_remove_challenge_no_perm(mock_mod, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await removecountingchallengechannel(admin_command_info, channel)
    admin_command_info.reply.assert_not_awaited()


@patch(
    "commands.minigames.counting_challenge.removecountingchannel.require_counting_channel",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "commands.minigames.counting_challenge.removecountingchannel.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_remove_challenge_no_channel(mock_mod, mock_req, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await removecountingchallengechannel(admin_command_info, channel)
    admin_command_info.reply.assert_not_awaited()


@patch(
    "commands.minigames.counting_modes.removecountingchannel.require_moderate_members",
    new_callable=AsyncMock,
    return_value=True,
)
async def test_remove_modes_no_perm(mock_mod, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await removecountingmodeschannel(admin_command_info, channel)
    admin_command_info.reply.assert_not_awaited()


@patch(
    "commands.minigames.counting_modes.removecountingchannel.require_counting_channel",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "commands.minigames.counting_modes.removecountingchannel.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_remove_modes_no_channel(mock_mod, mock_req, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await removecountingmodeschannel(admin_command_info, channel)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting_modes.removecountingchannel._repo")
@patch(
    "commands.minigames.counting_modes.removecountingchannel.require_counting_channel", new_callable=AsyncMock, return_value=2
)
@patch(
    "commands.minigames.counting_modes.removecountingchannel.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_remove_modes_counting_channel(mock_mod, mock_req, mock_repo, admin_command_info):
    mock_repo.clear = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    await removecountingmodeschannel(admin_command_info, channel)
    mock_repo.clear.assert_awaited_once()

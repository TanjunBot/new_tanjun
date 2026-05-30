from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.minigames.counting_challenge.setcountingprogress import setCountingProgress
from commands.minigames.counting_modes.setcountingprogress import setCountingProgress as setModesProgress
from tests.helpers.discord import make_text_channel

pytestmark = pytest.mark.asyncio


@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_moderate_members",
    new_callable=AsyncMock,
    return_value=True,
)
async def test_challenge_set_progress_no_perm(mock_mod, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setCountingProgress(admin_command_info, channel, 1)
    admin_command_info.reply.assert_not_awaited()


@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_counting_channel",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_challenge_set_progress_no_channel(mock_mod, mock_req, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setCountingProgress(admin_command_info, channel, 1)
    admin_command_info.reply.assert_not_awaited()


@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_valid_progress",
    new_callable=AsyncMock,
    return_value=True,
)
@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_counting_channel",
    new_callable=AsyncMock,
    return_value=1,
)
@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_challenge_set_progress_invalid(mock_mod, mock_req, mock_valid, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setCountingProgress(admin_command_info, channel, -1)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting_challenge.setcountingprogress._repo")
@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_valid_progress",
    new_callable=AsyncMock,
    return_value=False,
)
@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_counting_channel",
    new_callable=AsyncMock,
    return_value=3,
)
@patch(
    "commands.minigames.counting_challenge.setcountingprogress.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_challenge_set_progress_success(mock_mod, mock_req, mock_valid, mock_repo, admin_command_info):
    mock_repo.set_challenge_progress = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.send = AsyncMock()
    await setCountingProgress(admin_command_info, channel, 10)
    mock_repo.set_challenge_progress.assert_awaited_once()
    channel.send.assert_awaited_once()


@patch("commands.minigames.counting_modes.setcountingprogress._repo")
@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_valid_progress", new_callable=AsyncMock, return_value=False
)
@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_counting_channel", new_callable=AsyncMock, return_value=1
)
@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_modes_set_progress_success(mock_mod, mock_req, mock_valid, mock_repo, admin_command_info):
    mock_repo.set_challenge_progress = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.send = AsyncMock()
    await setModesProgress(admin_command_info, channel, 5)
    mock_repo.set_challenge_progress.assert_awaited_once()


@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_moderate_members", new_callable=AsyncMock, return_value=True
)
async def test_modes_set_progress_no_perm(mock_mod, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setModesProgress(admin_command_info, channel, 1)


@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_counting_channel", new_callable=AsyncMock, return_value=None
)
@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_modes_set_progress_no_channel(mock_mod, mock_req, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setModesProgress(admin_command_info, channel, 1)


@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_valid_progress", new_callable=AsyncMock, return_value=True
)
@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_counting_channel", new_callable=AsyncMock, return_value=1
)
@patch(
    "commands.minigames.counting_modes.setcountingprogress.require_moderate_members",
    new_callable=AsyncMock,
    return_value=False,
)
async def test_modes_set_progress_invalid(mock_mod, mock_req, mock_valid, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setModesProgress(admin_command_info, channel, -1)


@patch("commands.minigames.counting.setcountingprogress.require_moderate_members", new_callable=AsyncMock, return_value=True)
async def test_normal_set_progress_no_perm(mock_mod, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    from commands.minigames.counting.setcountingprogress import setCountingProgress as setNormalProgress

    await setNormalProgress(admin_command_info, channel, 1)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting.setcountingprogress.require_counting_channel", new_callable=AsyncMock, return_value=None)
@patch("commands.minigames.counting.setcountingprogress.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_normal_set_progress_no_channel(mock_mod, mock_req, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    from commands.minigames.counting.setcountingprogress import setCountingProgress as setNormalProgress

    await setNormalProgress(admin_command_info, channel, 1)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting.setcountingprogress.require_valid_progress", new_callable=AsyncMock, return_value=True)
@patch("commands.minigames.counting.setcountingprogress.require_counting_channel", new_callable=AsyncMock, return_value=1)
@patch("commands.minigames.counting.setcountingprogress.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_normal_set_progress_invalid(mock_mod, mock_req, mock_valid, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    from commands.minigames.counting.setcountingprogress import setCountingProgress as setNormalProgress

    await setNormalProgress(admin_command_info, channel, -1)
    admin_command_info.reply.assert_not_awaited()


@patch("commands.minigames.counting.setcountingprogress._repo")
@patch("commands.minigames.counting.setcountingprogress.require_valid_progress", new_callable=AsyncMock, return_value=False)
@patch("commands.minigames.counting.setcountingprogress.require_counting_channel", new_callable=AsyncMock, return_value=3)
@patch("commands.minigames.counting.setcountingprogress.require_moderate_members", new_callable=AsyncMock, return_value=False)
async def test_normal_set_progress_success(mock_mod, mock_req, mock_valid, mock_repo, admin_command_info):
    mock_repo.set_progress = AsyncMock()
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.send = AsyncMock()
    from commands.minigames.counting.setcountingprogress import setCountingProgress as setNormalProgress

    await setNormalProgress(admin_command_info, channel, 10)
    mock_repo.set_progress.assert_awaited_once()
    channel.send.assert_awaited_once()

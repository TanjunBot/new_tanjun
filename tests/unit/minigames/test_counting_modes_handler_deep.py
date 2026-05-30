from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from minigames import counting_modes as cm
from models import CountingMode
from tests.helpers.discord import make_guild, make_member, make_message


pytestmark = pytest.mark.asyncio


def _msg(content: str, user_id: int = 42):
    return make_message(content=content, author=make_member(user_id=user_id), guild=make_guild())


def _repo_async(mock_repo):
    mock_repo.clear = AsyncMock()
    mock_repo.set_mode_progress = AsyncMock()
    mock_repo.get_goal = AsyncMock(return_value=100)
    mock_repo.get_last_counter_id = AsyncMock(return_value="9")
    mock_repo.get_progress = AsyncMock(return_value=0)
    mock_repo.get_mode = AsyncMock(return_value=CountingMode.NORMAL)


@patch("minigames.counting_modes.repo")
async def test_counting_modes_wrong_empty(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.DiscordSafe.add_reaction", AsyncMock()),
        patch("minigames.counting_modes.DiscordSafe.reply", AsyncMock()) as reply,
        patch("minigames.counting_modes.random.choice", return_value=CountingMode.NORMAL),
        patch("minigames.counting_modes.get_goal", return_value=50),
    ):
        await cm.counting(_msg(""), config={"progress": 0, "mode": CountingMode.NORMAL, "goal": 50, "last_counter_id": "1"})
    mock_repo.clear.assert_awaited_once()
    reply.assert_awaited_once()


@patch("minigames.counting_modes.repo")
async def test_counting_modes_wrong_number(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.DiscordSafe.add_reaction", AsyncMock()),
        patch("minigames.counting_modes.DiscordSafe.reply", AsyncMock()),
        patch("minigames.counting_modes.random.choice", return_value=CountingMode.NORMAL),
        patch("minigames.counting_modes.get_goal", return_value=50),
    ):
        await cm.counting(_msg("99"), config={"progress": 0, "mode": CountingMode.NORMAL, "goal": 50, "last_counter_id": "1"})
    mock_repo.clear.assert_awaited_once()


@patch("minigames.counting_modes.repo")
async def test_counting_modes_double_count(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.DiscordSafe.add_reaction", AsyncMock()),
        patch("minigames.counting_modes.DiscordSafe.reply", AsyncMock()),
        patch("minigames.counting_modes.random.choice", return_value=CountingMode.NORMAL),
        patch("minigames.counting_modes.get_goal", return_value=50),
    ):
        await cm.counting(
            _msg("1", user_id=42),
            config={"progress": 0, "mode": CountingMode.NORMAL, "goal": 50, "last_counter_id": "42"},
        )
    mock_repo.clear.assert_awaited_once()


@patch("minigames.counting_modes.repo")
async def test_counting_modes_goal_reached(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.DiscordSafe.add_reaction", AsyncMock()),
        patch("minigames.counting_modes.DiscordSafe.reply", AsyncMock()),
        patch("minigames.counting_modes.random.choice", return_value=CountingMode.DOUBLE),
        patch("minigames.counting_modes.get_goal", return_value=1),
    ):
        await cm.counting(_msg("1"), config={"progress": 0, "mode": CountingMode.NORMAL, "goal": 1, "last_counter_id": "9"})
    mock_repo.clear.assert_awaited_once()


@patch("minigames.counting_modes.repo")
async def test_counting_modes_success_progress(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.random.randint", return_value=2),
    ):
        await cm.counting(_msg("1"))
    mock_repo.set_mode_progress.assert_awaited()


@patch("minigames.counting_modes.repo")
async def test_counting_modes_opted_out(mock_repo):
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=True)),
        patch("minigames.counting_modes.DiscordSafe.send_dm", AsyncMock()),
        patch("minigames.counting_modes.DiscordSafe.delete", AsyncMock()) as delete,
    ):
        await cm.counting(_msg("1"), config={"progress": 0, "mode": CountingMode.NORMAL, "goal": 50, "last_counter_id": "1"})
    delete.assert_awaited_once()


@patch("minigames.counting_modes.repo")
async def test_counting_modes_romean_success(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.random.randint", return_value=2),
    ):
        await cm.counting(
            _msg("I"),
            config={"progress": 0, "mode": CountingMode.ROMEAN, "goal": "X", "last_counter_id": "9", "guild_id": 1},
        )
    mock_repo.set_mode_progress.assert_awaited()


@patch("minigames.counting_modes.repo")
async def test_counting_modes_jackpot(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.random.randint", return_value=1),
    ):
        await cm.counting(_msg("1"))
    assert mock_repo.set_mode_progress.await_count >= 2


@patch("minigames.counting_modes.repo")
async def test_counting_modes_binary_invalid(mock_repo):
    _repo_async(mock_repo)
    with (
        patch("minigames.counting_modes.check_if_opted_out", AsyncMock(return_value=False)),
        patch("minigames.counting_modes.DiscordSafe.add_reaction", AsyncMock()),
        patch("minigames.counting_modes.DiscordSafe.reply", AsyncMock()),
        patch("minigames.counting_modes.random.choice", return_value=CountingMode.NORMAL),
        patch("minigames.counting_modes.get_goal", return_value=50),
    ):
        await cm.counting(_msg("notbinary"), config={"progress": 0, "mode": CountingMode.BINARY, "goal": 50, "last_counter_id": "1"})
    mock_repo.clear.assert_awaited_once()

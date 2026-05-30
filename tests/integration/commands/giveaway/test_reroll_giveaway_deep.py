from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.reroll_giveaway import perform_reroll, reroll_giveaway
from tests.helpers.discord import make_member
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _giveaway(**kwargs) -> MagicMock:
    gw = MagicMock()
    gw.guild_id = kwargs.get("guild_id", "123456789")
    gw.ended = kwargs.get("ended", True)
    gw.winners = kwargs.get("winners", 1)
    return gw


async def test_reroll_no_permission(restricted_command_info):
    await reroll_giveaway(restricted_command_info, 1)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.giveaway_service.get", new_callable=AsyncMock, return_value=None)
async def test_reroll_not_found(mock_get, admin_command_info):
    await reroll_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.giveaway_service.get", new_callable=AsyncMock)
async def test_reroll_wrong_guild(mock_get, admin_command_info):
    mock_get.return_value = _giveaway(guild_id="999")
    await reroll_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.giveaway_service.get", new_callable=AsyncMock)
async def test_reroll_not_ended(mock_get, admin_command_info):
    mock_get.return_value = _giveaway(ended=False, guild_id=str(admin_command_info.guild.id))
    await reroll_giveaway(admin_command_info, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.perform_reroll", new_callable=AsyncMock)
@patch("commands.giveaway.reroll_giveaway.giveaway_service.get", new_callable=AsyncMock)
async def test_reroll_single_winner_direct(mock_get, mock_perform, admin_command_info):
    mock_get.return_value = _giveaway(guild_id=str(admin_command_info.guild.id), winners=1)
    await reroll_giveaway(admin_command_info, 1)
    mock_perform.assert_awaited_once_with(admin_command_info, 1, 1)


async def _capture_reroll_view(admin_command_info, giveaway):
    captured: dict = {}
    real_reply = admin_command_info.reply

    async def capture_reply(*args, **kwargs):
        frame = inspect.currentframe()
        while frame is not None:
            if frame.f_code.co_name == "reroll_giveaway" and "RerollOptionsView" in frame.f_locals:
                captured["RerollOptionsView"] = frame.f_locals["RerollOptionsView"]
                break
            frame = frame.f_back
        return await real_reply(*args, **kwargs)

    admin_command_info.reply = AsyncMock(side_effect=capture_reply)
    with patch(
        "commands.giveaway.reroll_giveaway.giveaway_service.get",
        new_callable=AsyncMock,
        return_value=giveaway,
    ):
        await reroll_giveaway(admin_command_info, 1)
    return captured


@patch("commands.giveaway.reroll_giveaway.perform_reroll", new_callable=AsyncMock)
async def test_reroll_multi_winner_view(mock_perform, admin_command_info):
    gw = _giveaway(guild_id=str(admin_command_info.guild.id), winners=3)
    captured = await _capture_reroll_view(admin_command_info, gw)
    RerollOptionsView = captured["RerollOptionsView"]
    view = RerollOptionsView(admin_command_info, 1)

    one = make_view_interaction(admin_command_info.user)
    one.response.defer = AsyncMock()
    await view.reroll_one(one, MagicMock())
    mock_perform.assert_awaited_with(admin_command_info, 1, 1)

    mock_perform.reset_mock()
    all_interaction = make_view_interaction(admin_command_info.user)
    all_interaction.response.defer = AsyncMock()
    with patch(
        "commands.giveaway.reroll_giveaway.giveaway_service.get",
        new_callable=AsyncMock,
        return_value=gw,
    ):
        await view.reroll_all(all_interaction, MagicMock())
    mock_perform.assert_awaited_with(admin_command_info, 1, 3)

    denied = make_view_interaction(make_member(user_id=999))
    ok = await view.interaction_check(denied)
    assert ok is False


@patch("commands.giveaway.reroll_giveaway.giveaway_service.get_participants", new_callable=AsyncMock, return_value=[])
async def test_perform_reroll_no_participants(mock_parts, admin_command_info):
    await perform_reroll(admin_command_info, 1, 1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.giveaway.reroll_giveaway.random.choice", side_effect=["111", "222"])
@patch("commands.giveaway.reroll_giveaway.giveaway_service.get_participants", new_callable=AsyncMock)
async def test_perform_reroll_success(mock_parts, mock_choice, admin_command_info):
    mock_parts.return_value = ["111", "222", "333"]
    member = MagicMock()
    member.send = AsyncMock()
    admin_command_info.guild.get_member = MagicMock(return_value=member)
    await perform_reroll(admin_command_info, 1, 2)
    admin_command_info.reply.assert_awaited_once()
    assert member.send.await_count == 2


@patch("commands.giveaway.reroll_giveaway.giveaway_service.get", new_callable=AsyncMock, return_value=None)
@patch("commands.giveaway.reroll_giveaway.perform_reroll", new_callable=AsyncMock)
async def test_reroll_all_giveaway_gone(mock_perform, mock_get, admin_command_info):
    gw = _giveaway(guild_id=str(admin_command_info.guild.id), winners=3)
    captured = await _capture_reroll_view(admin_command_info, gw)
    view = captured["RerollOptionsView"](admin_command_info, 1)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.defer = AsyncMock()
    await view.reroll_all(interaction, MagicMock())
    admin_command_info.reply.assert_awaited()

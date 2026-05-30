from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games.flag_quiz import flag_quiz
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs.get("view")


@patch(
    "commands.games.flag_quiz.tanjunLocalizer.localize",
    side_effect=lambda _loc, key, **kw: key.split(".")[-1] if key.startswith("countries.") else key,
)
@patch("commands.games.flag_quiz.random_flag", return_value="germany.png")
async def test_flag_quiz_start(mock_flag, mock_loc, admin_command_info):
    await flag_quiz(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert _view_from_reply(admin_command_info) is not None


@patch(
    "commands.games.flag_quiz.tanjunLocalizer.localize",
    side_effect=lambda _loc, key, **kw: "Germany" if key.startswith("countries.") else key,
)
@patch("commands.games.flag_quiz.random_flag", return_value="germany.png")
async def test_flag_quiz_give_up(mock_flag, mock_loc, admin_command_info):
    await flag_quiz(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.followup.edit_message = AsyncMock()
    await view.give_up_button_callback(interaction, MagicMock())
    interaction.followup.edit_message.assert_awaited_once()


@patch(
    "commands.games.flag_quiz.tanjunLocalizer.localize",
    side_effect=lambda _loc, key, **kw: "Germany" if key.startswith("countries.") else key,
)
@patch("commands.games.flag_quiz.random_flag", return_value="germany.png")
async def test_flag_quiz_wrong_user(mock_flag, mock_loc, admin_command_info):
    await flag_quiz(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(user=MagicMock(id=999))
    await view.guess_button_callback(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


@patch(
    "commands.games.flag_quiz.tanjunLocalizer.localize",
    side_effect=lambda _loc, key, **kw: "Germany" if key.startswith("countries.") else key,
)
@patch("commands.games.flag_quiz.random_flag", return_value="germany.png")
async def test_flag_quiz_hint_once(mock_flag, mock_loc, admin_command_info):
    await flag_quiz(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.followup.edit_message = AsyncMock()
    await view.hint_button_callback(interaction, MagicMock())
    interaction.followup.edit_message.assert_awaited_once()


@patch(
    "commands.games.flag_quiz.tanjunLocalizer.localize",
    side_effect=lambda _loc, key, **kw: "Germany" if key.startswith("countries.") else key,
)
@patch("commands.games.flag_quiz.random_flag", return_value="germany.png")
async def test_flag_quiz_hint_twice(mock_flag, mock_loc, admin_command_info):
    await flag_quiz(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.followup.edit_message = AsyncMock()
    await view.hint_button_callback(interaction, MagicMock())
    interaction2 = make_view_interaction(admin_command_info.user)
    await view.hint_button_callback(interaction2, MagicMock())
    interaction2.followup.send.assert_awaited_once()


@patch(
    "commands.games.flag_quiz.tanjunLocalizer.localize",
    side_effect=lambda _loc, key, **kw: "Germany" if key.startswith("countries.") else key,
)
@patch("commands.games.flag_quiz.random_flag", return_value="germany.png")
async def test_flag_quiz_modal_correct_guess(mock_flag, mock_loc, admin_command_info):
    await flag_quiz(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.send_modal = AsyncMock()
    await view.guess_button_callback(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    submit = make_view_interaction(admin_command_info.user)
    submit.message = MagicMock(id=1)
    submit.followup.edit_message = AsyncMock()
    modal.children = [MagicMock(value="Germany")]
    await modal.on_submit(submit)
    submit.followup.edit_message.assert_awaited_once()


@patch(
    "commands.games.flag_quiz.tanjunLocalizer.localize",
    side_effect=lambda _loc, key, **kw: "Germany" if key.startswith("countries.") else key,
)
@patch("commands.games.flag_quiz.random_flag", return_value="germany.png")
async def test_flag_quiz_modal_wrong_guess(mock_flag, mock_loc, admin_command_info):
    await flag_quiz(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.send_modal = AsyncMock()
    await view.guess_button_callback(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    submit = make_view_interaction(admin_command_info.user)
    submit.message = MagicMock(id=1)
    submit.followup.edit_message = AsyncMock()
    modal.children = [MagicMock(value="France")]
    await modal.on_submit(submit)
    submit.followup.edit_message.assert_awaited_once()

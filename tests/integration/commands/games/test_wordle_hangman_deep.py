from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from commands.games.hangman import hangman
from commands.games.wordle import wordle
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs.get("view")


async def _start_wordle_game(info):
    png = io.BytesIO(b"\x89PNG\r\n\x1a\n\xff")
    with patch("commands.games.wordle.random.choice", return_value="about"):
        with patch("commands.games.wordle.generate_wordle_image", AsyncMock(return_value=png)):
            await wordle(info, "en")
    start_view = _view_from_reply(info)
    interaction = make_view_interaction(info.user)
    interaction.response.edit_message = AsyncMock()
    await start_view.normal_button_callback(interaction, MagicMock())
    return interaction.response.edit_message.await_args.kwargs["view"], interaction


@patch("commands.games.wordle.random.choice", return_value="about")
async def test_wordle_start(mock_choice, admin_command_info):
    png = io.BytesIO(b"\x89PNG\r\n\x1a\n\xff")
    with patch("commands.games.wordle.generate_wordle_image", AsyncMock(return_value=png)):
        await wordle(admin_command_info, "en")
    admin_command_info.reply.assert_awaited_once()
    assert _view_from_reply(admin_command_info) is not None


async def test_wordle_give_up(admin_command_info):
    view, interaction = await _start_wordle_game(admin_command_info)
    await view.give_up_button_callback(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited()


async def test_wordle_wrong_user(admin_command_info):
    view, _interaction = await _start_wordle_game(admin_command_info)
    wrong = make_view_interaction(MagicMock(id=99999))
    await view.guess_button_callback(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_start(mock_choice, admin_command_info):
    await hangman(admin_command_info, "en")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_give_up(mock_choice, admin_command_info):
    await hangman(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.give_up_button_callback(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


async def test_wordle_correct_guess(admin_command_info):
    view, interaction = await _start_wordle_game(admin_command_info)
    await view.guess_button_callback(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.children[0].value = "about"
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    interaction.response.edit_message.assert_awaited_once()


async def test_wordle_invalid_guess(admin_command_info):
    view, interaction = await _start_wordle_game(admin_command_info)
    await view.guess_button_callback(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.children[0].value = "zzzzz"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_correct_guess(mock_choice, admin_command_info):
    await hangman(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    await view.guess_button_callback(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.children[0].value = "about"
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_wrong_user(mock_choice, admin_command_info):
    await hangman(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(MagicMock(id=99999))
    await view.guess_button_callback(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()

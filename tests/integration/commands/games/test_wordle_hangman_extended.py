from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games.hangman import get_guessed_letters, hangman, wrong_letters
from commands.games.wordle import wordle
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction
from tests.integration.commands.games.test_wordle_hangman_deep import _start_wordle_game, _view_from_reply


def test_get_guessed_letters_partial():
    assert get_guessed_letters(["a"], "about") == "a____"


def test_get_guessed_letters_space():
    assert get_guessed_letters([], "a b") == "_ _"


def test_wrong_letters_count():
    assert wrong_letters(["z", "y", "x"], "about") == 3


pytestmark = pytest.mark.asyncio


@patch("commands.games.wordle.random.choice", return_value="about")
async def test_wordle_locale_en_us(mock_choice, admin_command_info):
    png = io.BytesIO(b"\x89PNG\r\n\x1a\n\xff")
    with patch("commands.games.wordle.generate_wordle_image", AsyncMock(return_value=png)):
        await wordle(admin_command_info, "en-US")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.games.wordle.random.choice", return_value="about")
async def test_wordle_locale_pt_br(mock_choice, admin_command_info):
    png = io.BytesIO(b"\x89PNG\r\n\x1a\n\xff")
    with patch("commands.games.wordle.generate_wordle_image", AsyncMock(return_value=png)):
        await wordle(admin_command_info, "pt-BR")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.games.wordle.random.choice", return_value="about")
async def test_wordle_ja_extra_description(mock_choice, admin_command_info):
    png = io.BytesIO(b"\x89PNG\r\n\x1a\n\xff")
    with patch("commands.games.wordle.generate_wordle_image", AsyncMock(return_value=png)):
        await wordle(admin_command_info, "ja")
    admin_command_info.reply.assert_awaited_once()


async def test_wordle_six_wrong_guesses(admin_command_info):
    view, interaction = await _start_wordle_game(admin_command_info)
    for guess in ["apple", "grape", "peach", "berry", "melon", "fruit"]:
        interaction = make_view_interaction(admin_command_info.user)
        await view.guess_button_callback(interaction, MagicMock())
        modal = interaction.response.send_modal.await_args.args[0]
        modal.children[0].value = guess
        interaction.response.edit_message = AsyncMock()
        await modal.on_submit(interaction)
    interaction.response.edit_message.assert_awaited()


async def test_wordle_give_up_wrong_user(admin_command_info):
    view, _interaction = await _start_wordle_game(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view.give_up_button_callback(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_locale_es(mock_choice, admin_command_info):
    await hangman(admin_command_info, "es-ES")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_wrong_multi_char_guess(mock_choice, admin_command_info):
    await hangman(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    await view.guess_button_callback(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.children[0].value = "wrongword"
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_too_many_wrong_letters(mock_choice, admin_command_info):
    await hangman(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    wrong_letters_list = list("zyxwvutsrqp")
    for letter in wrong_letters_list:
        interaction = make_view_interaction(admin_command_info.user)
        await view.guess_button_callback(interaction, MagicMock())
        modal = interaction.response.send_modal.await_args.args[0]
        modal.children[0].value = letter
        interaction.response.edit_message = AsyncMock()
        await modal.on_submit(interaction)
    interaction.response.edit_message.assert_awaited()


@patch("commands.games.hangman.random.choice", return_value="about")
async def test_hangman_give_up_wrong_user(mock_choice, admin_command_info):
    await hangman(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view.give_up_button_callback(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_wordle_image():
    from commands.games.wordle import generate_wordle_image

    buf = await generate_wordle_image(["about"], "about", language="en")
    assert buf.getvalue()[:8] == b"\x89PNG\r\n\x1a\n"

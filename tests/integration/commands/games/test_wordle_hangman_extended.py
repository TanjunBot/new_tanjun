from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from commands.games.hangman import get_guessed_letters, hangman, wrong_letters
from commands.games.wordle import generate_wordle_background, wordle
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs.get("view")


def test_get_guessed_letters_partial():
    assert get_guessed_letters(["a"], "about") == "a____"


def test_get_guessed_letters_space():
    assert get_guessed_letters([], "a b") == "_ _"


def test_wrong_letters_count():
    assert wrong_letters(["z", "y", "x"], "about") == 3


pytestmark = pytest.mark.asyncio


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_locale_en_us(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en-US")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_locale_pt_br(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "pt-BR")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_ja_extra_description(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "ja")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_six_wrong_guesses(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    for guess in ["apple", "grape", "peach", "berry", "melon", "fruit"]:
        interaction = make_view_interaction(admin_command_info.user)
        await view.guess_button_callback(interaction, MagicMock())
        modal = interaction.response.send_modal.await_args.args[0]
        modal.children[0].value = guess
        interaction.response.edit_message = AsyncMock()
        await modal.on_submit(interaction)
    interaction.response.edit_message.assert_awaited()


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_give_up_wrong_user(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
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


def test_generate_wordle_background(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    generate_wordle_background()
    assert (tmp_path / "wordle_background.png").exists()

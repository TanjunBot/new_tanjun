from __future__ import annotations

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


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_start(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en")
    admin_command_info.reply.assert_awaited_once()
    assert _view_from_reply(admin_command_info) is not None


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_give_up(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    for child in view.children:
        if hasattr(child, "callback") and "give" in getattr(child, "label", "").lower():
            await child.callback(interaction, MagicMock())
            break
    else:
        await view.give_up_button_callback(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_wrong_user(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
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


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_correct_guess(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    await view.guess_button_callback(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args.args[0]
    modal.children[0].value = "about"
    interaction.response.edit_message = AsyncMock()
    await modal.on_submit(interaction)
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.games.wordle.random.choice", return_value="about")
@patch("commands.games.wordle.Image.open")
async def test_wordle_invalid_guess(mock_open, mock_choice, admin_command_info):
    img = Image.new("RGBA", (500, 600), (20, 20, 20, 255))
    mock_open.return_value = img.copy()
    await wordle(admin_command_info, "en")
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
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

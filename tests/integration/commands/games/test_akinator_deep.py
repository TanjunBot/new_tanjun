from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games.akinator import akinator
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


class _FakeAki:
    question = "Is it a character?"
    progression = 50
    akitude = "http://example.com/q.png"
    answer_id = None
    name = "Mario"
    description = "Plumber"
    photo = "http://example.com/mario.png"
    step = 5

    def start_game(self):
        pass

    def post_answer(self, answer):
        if answer == "y":
            self.answer_id = 1

    def go_back(self):
        pass


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs.get("view")


@patch("commands.games.akinator.Akinator", return_value=_FakeAki())
async def test_akinator_start(mock_cls, admin_command_info):
    await akinator(admin_command_info, "Characters")
    admin_command_info.reply.assert_awaited_once()
    assert _view_from_reply(admin_command_info) is not None


@patch("commands.games.akinator.Akinator", return_value=_FakeAki())
async def test_akinator_yes_answer(mock_cls, admin_command_info):
    await akinator(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.response.defer = AsyncMock()
    interaction.followup.edit_message = AsyncMock()
    await view.akinator_yes(interaction, MagicMock())
    interaction.followup.edit_message.assert_awaited_once()


@patch("commands.games.akinator.Akinator", return_value=_FakeAki())
async def test_akinator_no_wrong_user(mock_cls, admin_command_info):
    await akinator(admin_command_info)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(MagicMock(id=99999))
    wrong.response.defer = AsyncMock()
    wrong.followup.send = AsyncMock()
    await view.akinator_no(wrong, MagicMock())
    wrong.followup.send.assert_awaited_once()


@patch("commands.games.akinator.Akinator", return_value=_FakeAki())
async def test_akinator_idk(mock_cls, admin_command_info):
    await akinator(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.response.defer = AsyncMock()
    interaction.followup.edit_message = AsyncMock()
    await view.akinator_idk(interaction, MagicMock())
    interaction.followup.edit_message.assert_awaited_once()


@patch("commands.games.akinator.Akinator", return_value=_FakeAki())
async def test_akinator_probably_and_back(mock_cls, admin_command_info):
    await akinator(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.response.defer = AsyncMock()
    interaction.followup.edit_message = AsyncMock()
    await view.akinator_probably(interaction, MagicMock())
    await view.akinator_back(interaction, MagicMock())
    assert interaction.followup.edit_message.await_count == 2


@patch("commands.games.akinator.Akinator", return_value=_FakeAki())
async def test_akinator_german_locale(mock_cls, admin_command_info):
    admin_command_info.locale = "de"
    await akinator(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@pytest.mark.parametrize(
    "locale,expected_lang",
    [
        ("fr", "fr"),
        ("ja", "jp"),
        ("ko", "ko"),
        ("ru", "ru"),
        ("zh-CN", "zh"),
        ("es-ES", "es"),
        ("pt-BR", "pt"),
        ("tr", "tr"),
        ("id", "id"),
        ("pl", "pl"),
        ("nl", "nl"),
        ("he", "he"),
        ("ar", "ar"),
    ],
)
@patch("commands.games.akinator.Akinator")
async def test_akinator_locales(mock_cls, locale, expected_lang, admin_command_info):
    mock_cls.return_value = _FakeAki()
    admin_command_info.locale = locale
    await akinator(admin_command_info)
    assert mock_cls.call_args.kwargs["lang"] == expected_lang


@patch("commands.games.akinator.Akinator", return_value=_FakeAki())
async def test_akinator_probably_not(mock_cls, admin_command_info):
    await akinator(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.response.defer = AsyncMock()
    interaction.followup.edit_message = AsyncMock()
    await view.akinator_probably_not(interaction, MagicMock())
    interaction.followup.edit_message.assert_awaited_once()

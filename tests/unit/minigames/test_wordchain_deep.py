from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from minigames import wordchain


pytestmark = pytest.mark.asyncio


def _message(content="word", guild=None, author_id=1):
    msg = MagicMock()
    msg.content = content
    msg.channel = MagicMock(id=100)
    msg.author = MagicMock(id=author_id)
    msg.guild = guild
    return msg


@patch("minigames.wordchain.DiscordSafe.send", new_callable=AsyncMock)
async def test_wordchain_no_guild(mock_send):
    await wordchain.wordchain(_message(guild=None))
    mock_send.assert_awaited_once()


@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value=None)
async def test_wordchain_no_active(mock_get):
    guild = MagicMock(preferred_locale="en_US")
    await wordchain.wordchain(_message(guild=guild))
    mock_get.assert_awaited_once()


@patch("minigames.wordchain.DiscordSafe.delete", new_callable=AsyncMock)
@patch("minigames.wordchain.DiscordSafe.send_dm", new_callable=AsyncMock)
@patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=True)
@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="Start")
async def test_wordchain_opted_out(mock_word, mock_opt, mock_dm, mock_del):
    guild = MagicMock(preferred_locale="en_US")
    await wordchain.wordchain(_message(guild=guild))
    mock_dm.assert_awaited_once()
    mock_del.assert_awaited_once()


@patch("minigames.wordchain.DiscordSafe.delete", new_callable=AsyncMock)
@patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="Start")
async def test_wordchain_empty_content(mock_word, mock_opt, mock_del):
    guild = MagicMock(preferred_locale="en_US")
    await wordchain.wordchain(_message(content="", guild=guild))
    mock_del.assert_awaited_once()


@patch("minigames.wordchain.DiscordSafe.delete", new_callable=AsyncMock)
@patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="Start")
async def test_wordchain_multi_word(mock_word, mock_opt, mock_del):
    guild = MagicMock(preferred_locale="en_US")
    await wordchain.wordchain(_message(content="two words", guild=guild))
    mock_del.assert_awaited_once()


@patch("minigames.wordchain.DiscordSafe.delete", new_callable=AsyncMock)
@patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="1")
@patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="Start")
async def test_wordchain_same_user(mock_word, mock_opt, mock_last, mock_del):
    guild = MagicMock(preferred_locale="en_US")
    await wordchain.wordchain(_message(content="next", guild=guild, author_id=1))
    mock_del.assert_awaited_once()


@patch("minigames.wordchain.DiscordSafe.send", new_callable=AsyncMock)
@patch("minigames.wordchain.set_wordchain_word", new_callable=AsyncMock)
@patch("minigames.wordchain.clear_wordchain", new_callable=AsyncMock)
@patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="2")
@patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="Start")
async def test_wordchain_sentence_end(mock_word, mock_opt, mock_last, mock_clear, mock_set, mock_send):
    guild = MagicMock(id=5, preferred_locale="en_US")
    await wordchain.wordchain(_message(content="end.", guild=guild, author_id=1))
    mock_clear.assert_awaited_once()
    mock_send.assert_awaited_once()


@patch("minigames.wordchain.set_wordchain_word", new_callable=AsyncMock)
@patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="2")
@patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="Start")
async def test_wordchain_comma_only(mock_word, mock_opt, mock_last, mock_set):
    guild = MagicMock(id=5, preferred_locale="en_US")
    await wordchain.wordchain(_message(content=",", guild=guild, author_id=1))
    mock_set.assert_awaited_once()


@patch("minigames.wordchain.set_wordchain_word", new_callable=AsyncMock)
@patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="2")
@patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="Start")
async def test_wordchain_append_word(mock_word, mock_opt, mock_last, mock_set):
    guild = MagicMock(id=5, preferred_locale="en_US")
    await wordchain.wordchain(_message(content="next", guild=guild, author_id=1))
    mock_set.assert_awaited_once()

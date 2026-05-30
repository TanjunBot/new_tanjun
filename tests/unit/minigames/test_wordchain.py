"""Unit tests for wordchain minigame."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from minigames.wordchain import wordchain
from tests.helpers.discord import make_guild, make_member, make_message


@pytest.mark.unit
class TestWordchain:
    @pytest.mark.asyncio
    async def test_ignores_dm(self):
        message = make_message()
        message.guild = None
        with patch("minigames.wordchain.DiscordSafe.send", new_callable=AsyncMock) as send:
            await wordchain(message)
            send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_no_active_wordchain_returns_early(self):
        message = make_message(content="hello")
        with patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value=None):
            await wordchain(message)

    @pytest.mark.asyncio
    async def test_multi_word_message_deleted(self):
        message = make_message(content="hello world")
        with (
            patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="start"),
            patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="0"),
            patch("minigames.wordchain.DiscordSafe.delete", new_callable=AsyncMock) as delete,
        ):
            await wordchain(message)
        delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_same_user_twice_deleted(self):
        author = make_member(user_id=55)
        message = make_message(content="next", author=author)
        with (
            patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="start"),
            patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="55"),
            patch("minigames.wordchain.DiscordSafe.delete", new_callable=AsyncMock) as delete,
        ):
            await wordchain(message)
        delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sentence_end_clears_chain(self):
        guild = make_guild()
        guild.preferred_locale = "en-US"
        message = make_message(content="end.", guild=guild)
        with (
            patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="The"),
            patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="1"),
            patch("minigames.wordchain.clear_wordchain", new_callable=AsyncMock) as clear,
            patch("minigames.wordchain.set_wordchain_word", new_callable=AsyncMock) as set_word,
            patch("minigames.wordchain.DiscordSafe.send", new_callable=AsyncMock),
        ):
            await wordchain(message)
        clear.assert_awaited_once()
        set_word.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_comma_appends_without_author(self):
        guild = make_guild()
        message = make_message(content=",", guild=guild)
        with (
            patch("minigames.wordchain.get_wordchain_word", new_callable=AsyncMock, return_value="word"),
            patch("minigames.wordchain.check_if_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames.wordchain.get_wordchain_last_user_id", new_callable=AsyncMock, return_value="1"),
            patch("minigames.wordchain.set_wordchain_word", new_callable=AsyncMock) as set_word,
        ):
            await wordchain(message)
        set_word.assert_awaited_once()
        assert set_word.await_args.kwargs["worder_id"] == "nobody"

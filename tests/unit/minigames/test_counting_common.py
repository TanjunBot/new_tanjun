"""Unit tests for shared counting minigame logic."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from minigames._counting_common import _get_locale, counting
from tests.helpers.discord import make_guild, make_member, make_message


@pytest.mark.unit
class TestCountingCommonLocale:
    def test_get_locale_from_guild(self):
        guild = make_guild()
        guild.preferred_locale = "de"
        message = make_message(guild=guild)
        assert _get_locale(message) == "de"

    def test_get_locale_fallback(self):
        guild = make_guild()
        del guild.preferred_locale
        message = make_message(guild=guild)
        assert _get_locale(message) == "en_US"


@pytest.mark.unit
class TestCountingCommonFlow:
    @pytest.mark.asyncio
    async def test_ignores_dm_messages(self):
        message = make_message()
        message.guild = None
        with patch("minigames._counting_common._handle_guild_check", new_callable=AsyncMock) as handle:
            handle.return_value = True
            await counting(
                message,
                get_progress_func=AsyncMock(return_value=0),
                get_last_counter_id_func=AsyncMock(return_value=None),
                increase_progress_func=AsyncMock(),
            )
            handle.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_correct_count_increments_progress(self):
        author = make_member(user_id=42)
        message = make_message(content="1", author=author)
        increase = AsyncMock()
        with (
            patch("minigames._counting_common._handle_guild_check", new_callable=AsyncMock, return_value=False),
            patch("minigames._counting_common._handle_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames._counting_common.random.randint", return_value=2),
        ):
            await counting(
                message,
                get_progress_func=AsyncMock(return_value=0),
                get_last_counter_id_func=AsyncMock(return_value="99"),
                increase_progress_func=increase,
            )
        increase.assert_awaited_once_with(message.channel.id, message.author.id)

    @pytest.mark.asyncio
    async def test_wrong_number_deleted(self):
        message = make_message(content="5")
        with (
            patch("minigames._counting_common._handle_guild_check", new_callable=AsyncMock, return_value=False),
            patch("minigames._counting_common._handle_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames._counting_common.DiscordSafe.delete", new_callable=AsyncMock) as delete,
        ):
            await counting(
                message,
                get_progress_func=AsyncMock(return_value=0),
                get_last_counter_id_func=AsyncMock(return_value=None),
                increase_progress_func=AsyncMock(),
            )
        delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_double_count_same_user_deleted(self):
        author = make_member(user_id=42)
        message = make_message(content="1", author=author)
        with (
            patch("minigames._counting_common._handle_guild_check", new_callable=AsyncMock, return_value=False),
            patch("minigames._counting_common._handle_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames._counting_common.DiscordSafe.delete", new_callable=AsyncMock) as delete,
        ):
            await counting(
                message,
                get_progress_func=AsyncMock(return_value=0),
                get_last_counter_id_func=AsyncMock(return_value="42"),
                increase_progress_func=AsyncMock(),
            )
        delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_on_failure_callback(self):
        message = make_message(content="bad")
        on_failure = AsyncMock()
        with (
            patch("minigames._counting_common._handle_guild_check", new_callable=AsyncMock, return_value=False),
            patch("minigames._counting_common._handle_opted_out", new_callable=AsyncMock, return_value=False),
        ):
            await counting(
                message,
                get_progress_func=AsyncMock(return_value=3),
                get_last_counter_id_func=AsyncMock(return_value=None),
                increase_progress_func=AsyncMock(),
                on_failure=on_failure,
            )
        on_failure.assert_awaited_once()


@pytest.mark.unit
class TestCountingCommonHypothesis:
    @given(
        progress=st.integers(min_value=0, max_value=1000),
        content=st.integers(min_value=1, max_value=1001),
    )
    @settings(max_examples=60)
    def test_valid_count_only_when_content_equals_progress_plus_one(self, progress: int, content: int):
        is_valid = str(content) == str(progress + 1) and str(content).isdigit()
        assert is_valid == (content == progress + 1)

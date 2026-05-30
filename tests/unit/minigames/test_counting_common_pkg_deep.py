from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from minigames import _counting_common as pkg
from tests.helpers.discord import make_guild, make_member, make_message

pytestmark = pytest.mark.asyncio


async def test_handle_guild_check_no_guild():
    message = make_message()
    message.guild = None
    with patch("minigames._counting_common.DiscordSafe.send", AsyncMock()) as send:
        assert await pkg._handle_guild_check(message) is True
    send.assert_awaited_once()


async def test_handle_guild_check_with_guild():
    message = make_message(guild=make_guild())
    assert await pkg._handle_guild_check(message) is False


async def test_handle_opted_out_false():
    message = make_message(guild=make_guild())
    with patch("minigames._counting_common.check_if_opted_out", AsyncMock(return_value=False)):
        assert await pkg._handle_opted_out(message, "en") is False


async def test_counting_progress_none_early_return():
    message = make_message(content="1", guild=make_guild())
    increase = AsyncMock()
    with (
        patch("minigames._counting_common._handle_guild_check", AsyncMock(return_value=False)),
        patch("minigames._counting_common._handle_opted_out", AsyncMock(return_value=False)),
    ):
        await pkg.counting(
            message,
            get_progress_func=AsyncMock(return_value=None),
            get_last_counter_id_func=AsyncMock(),
            increase_progress_func=increase,
        )
    increase.assert_not_awaited()


async def test_counting_with_config_progress_none():
    message = make_message(content="1", guild=make_guild())
    with (
        patch("minigames._counting_common._handle_guild_check", AsyncMock(return_value=False)),
        patch("minigames._counting_common._handle_opted_out", AsyncMock(return_value=False)),
    ):
        await pkg.counting(
            message,
            get_progress_func=AsyncMock(),
            get_last_counter_id_func=AsyncMock(),
            increase_progress_func=AsyncMock(),
            config={"progress": None},
        )


async def test_counting_empty_with_on_failure():
    message = make_message(content="", guild=make_guild())
    on_failure = AsyncMock()
    with (
        patch("minigames._counting_common._handle_guild_check", AsyncMock(return_value=False)),
        patch("minigames._counting_common._handle_opted_out", AsyncMock(return_value=False)),
    ):
        await pkg.counting(
            message,
            get_progress_func=AsyncMock(return_value=0),
            get_last_counter_id_func=AsyncMock(return_value=None),
            increase_progress_func=AsyncMock(),
            on_failure=on_failure,
        )
    on_failure.assert_awaited_once()


async def test_counting_non_digit_with_on_failure():
    message = make_message(content="abc", guild=make_guild())
    on_failure = AsyncMock()
    with (
        patch("minigames._counting_common._handle_guild_check", AsyncMock(return_value=False)),
        patch("minigames._counting_common._handle_opted_out", AsyncMock(return_value=False)),
    ):
        await pkg.counting(
            message,
            get_progress_func=AsyncMock(return_value=0),
            get_last_counter_id_func=AsyncMock(return_value=None),
            increase_progress_func=AsyncMock(),
            on_failure=on_failure,
        )
    on_failure.assert_awaited_once()


async def test_counting_wrong_number_with_on_failure():
    message = make_message(content="5", guild=make_guild())
    on_failure = AsyncMock()
    with (
        patch("minigames._counting_common._handle_guild_check", AsyncMock(return_value=False)),
        patch("minigames._counting_common._handle_opted_out", AsyncMock(return_value=False)),
    ):
        await pkg.counting(
            message,
            get_progress_func=AsyncMock(return_value=0),
            get_last_counter_id_func=AsyncMock(return_value=None),
            increase_progress_func=AsyncMock(),
            on_failure=on_failure,
        )
    on_failure.assert_awaited_once()


async def test_counting_double_with_on_double_count():
    author = make_member(user_id=42)
    message = make_message(content="1", author=author, guild=make_guild())
    on_double = AsyncMock()
    with (
        patch("minigames._counting_common._handle_guild_check", AsyncMock(return_value=False)),
        patch("minigames._counting_common._handle_opted_out", AsyncMock(return_value=False)),
    ):
        await pkg.counting(
            message,
            get_progress_func=AsyncMock(return_value=0),
            get_last_counter_id_func=AsyncMock(return_value="42"),
            increase_progress_func=AsyncMock(),
            on_double_count=on_double,
            config={"progress": 0, "last_counter_id": "42"},
        )
    on_double.assert_awaited_once()


async def test_counting_jackpot():
    author = make_member(user_id=42)
    message = make_message(content="1", author=author, guild=make_guild())
    increase = AsyncMock()
    with (
        patch("minigames._counting_common._handle_guild_check", AsyncMock(return_value=False)),
        patch("minigames._counting_common._handle_opted_out", AsyncMock(return_value=False)),
        patch("minigames._counting_common.random.randint", return_value=1),
        patch("minigames._counting_common.DiscordSafe.send", AsyncMock()) as send,
    ):
        await pkg.counting(
            message,
            get_progress_func=AsyncMock(return_value=0),
            get_last_counter_id_func=AsyncMock(return_value="99"),
            increase_progress_func=increase,
        )
    assert increase.await_count >= 2
    send.assert_awaited_once()

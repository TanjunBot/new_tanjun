"""Tests for the dispatcher priority ordering."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from utils.dispatcher import (
    MessageFilters,
    Priority,
    clear,
    dispatch,
    register,
    registered_handlers,
)


@pytest.fixture(autouse=True)
def reset_registry() -> None:
    clear()


def _make_message(
    author_bot: bool = False,
    guild: MagicMock | None = None,
    channel_id: int = 100,
) -> MagicMock:
    message = MagicMock(spec=["author", "guild", "channel", "id"])
    message.author = MagicMock()
    message.author.bot = author_bot
    message.guild = guild
    message.channel = MagicMock()
    message.channel.id = channel_id
    message.id = 12345
    return message


# ------------------------------------------------------------------
# Priority constants
# ------------------------------------------------------------------


class TestPriorityConstants:
    def test_values_ordered(self) -> None:
        assert Priority.CRITICAL < Priority.HIGH < Priority.NORMAL < Priority.LOW < Priority.BACKGROUND


# ------------------------------------------------------------------
# Registration ordering
# ------------------------------------------------------------------


class TestRegistrationOrderByPriority:
    async def test_handlers_sorted_on_register(self) -> None:
        """Handlers should be sorted by priority when registered, not just at dispatch time."""

        async def high(_m: object) -> None: ...
        async def normal(_m: object) -> None: ...
        async def low(_m: object) -> None: ...

        register(normal, name="normal", priority=Priority.NORMAL)
        register(high, name="high", priority=Priority.HIGH)
        register(low, name="low", priority=Priority.LOW)

        handlers = registered_handlers()
        names = [h.name for h in handlers]
        assert names == ["high", "normal", "low"], f"Expected high → normal → low, got {names}"

    async def test_dispatch_order_by_priority(self) -> None:
        """Dispatch should execute handlers in priority order."""
        execution_order: list[str] = []

        async def critical_handler(_m: object) -> None:
            execution_order.append("critical")

        async def normal_handler(_m: object) -> None:
            execution_order.append("normal")

        async def background_handler(_m: object) -> None:
            execution_order.append("background")

        register(critical_handler, name="critical", priority=Priority.CRITICAL)
        register(normal_handler, name="normal", priority=Priority.NORMAL)
        register(background_handler, name="background", priority=Priority.BACKGROUND)

        mock_msg = _make_message(guild=MagicMock())
        await dispatch(mock_msg)
        expected = ["critical", "normal", "background"]
        assert execution_order == expected, f"Wrong order: {execution_order}"

    async def test_same_priority_preserves_insertion_order(self) -> None:
        """Handlers with same priority should maintain insertion order."""

        async def first(_m: object) -> None: ...
        async def second(_m: object) -> None: ...
        async def third(_m: object) -> None: ...

        register(first, name="first", priority=Priority.NORMAL)
        register(second, name="second", priority=Priority.NORMAL)
        register(third, name="third", priority=Priority.NORMAL)

        handlers = registered_handlers()
        names = [h.name for h in handlers]
        assert names == ["first", "second", "third"], f"Expected insertion order, got {names}"


# ------------------------------------------------------------------
# Filtering
# ------------------------------------------------------------------


class TestFiltering:
    async def test_ignore_bots(self) -> None:
        async def handler(_m: object) -> None:
            pass

        register(handler, name="bot_safe",
                 filters=MessageFilters(ignore_bots=True))
        bot_msg = _make_message(author_bot=True, guild=MagicMock())
        user_msg = _make_message(author_bot=False, guild=MagicMock())

        assert not registered_handlers()[0].filters.check(bot_msg)
        assert registered_handlers()[0].filters.check(user_msg)

    async def test_only_guilds(self) -> None:
        async def handler(_m: object) -> None:
            pass

        register(handler, name="guild_only",
                 filters=MessageFilters(only_guilds=True))
        dm_msg = _make_message(guild=None)
        guild_msg = _make_message(guild=MagicMock())

        assert not registered_handlers()[0].filters.check(dm_msg)
        assert registered_handlers()[0].filters.check(guild_msg)

    async def test_channel_whitelist(self) -> None:
        async def handler(_m: object) -> None:
            pass

        register(handler, name="channel_limited",
                 filters=MessageFilters(channel_whitelist={100, 200}))

        matching = _make_message(guild=MagicMock(), channel_id=100)
        blocked = _make_message(guild=MagicMock(), channel_id=300)

        assert registered_handlers()[0].filters.check(matching)
        assert not registered_handlers()[0].filters.check(blocked)

    async def test_channel_blacklist(self) -> None:
        async def handler(_m: object) -> None:
            pass

        register(handler, name="channel_blocked",
                 filters=MessageFilters(channel_blacklist={999}))

        allowed = _make_message(guild=MagicMock(), channel_id=100)
        blocked = _make_message(guild=MagicMock(), channel_id=999)

        assert registered_handlers()[0].filters.check(allowed)
        assert not registered_handlers()[0].filters.check(blocked)


# ------------------------------------------------------------------
# Dispatch smoke tests
# ------------------------------------------------------------------


pytestmark = pytest.mark.asyncio


class TestDispatch:
    async def test_dispatch_no_handlers(self) -> None:
        clear()
        results = await dispatch(_make_message(guild=MagicMock()))
        assert results == []

    async def test_dispatch_single_handler(self) -> None:
        processed = False

        async def handler(_m: object) -> None:
            nonlocal processed
            processed = True

        register(handler, name="single")
        await dispatch(_make_message(guild=MagicMock()))
        assert processed

    async def test_dispatch_filter_blocks(self) -> None:
        """Handler should not run when its filter rejects the message."""
        processed = False

        async def guild_only(_m: object) -> None:
            nonlocal processed
            processed = True

        register(guild_only, name="guild_only",
                 filters=MessageFilters(only_guilds=True))

        # DM message should be blocked by guild_only filter
        dm_msg = _make_message(guild=None)
        await dispatch(dm_msg)
        assert processed is False, "Handler should not have run for DM message"

        # Guild message should pass the filter
        guild_msg = _make_message(guild=MagicMock())
        await dispatch(guild_msg)
        assert processed is True, "Handler should have run for guild message"

    async def test_handler_exception_does_not_block_others(self) -> None:
        """A handler that raises should not prevent other handlers from running."""
        processed: list[str] = []

        async def failing(_m: object) -> None:
            raise ValueError("Boom!")

        async def ok_handler(_m: object) -> None:
            processed.append("ok")

        register(failing, name="failing", priority=Priority.HIGH)
        register(ok_handler, name="ok", priority=Priority.NORMAL)

        results = await dispatch(_make_message(guild=MagicMock()))
        assert "ok" in processed
        assert len(results) == 2
        failing_name, failing_result = results[0]
        assert isinstance(failing_result, ValueError)

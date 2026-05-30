"""Tests for the utils/dispatcher.py module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from utils.dispatcher import HandlerRegistry, MessageHandler, register_handler
from utils.dispatcher import registry as _global_registry

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def fresh_registry() -> HandlerRegistry:
    """Return a clean HandlerRegistry (no pre-registered handlers)."""
    return HandlerRegistry()


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
# MessageHandler dataclass
# ------------------------------------------------------------------


class TestMessageHandler:
    """Basic structural tests for MessageHandler."""

    def test_defaults(self) -> None:
        handler = MessageHandler(name="test", callback=lambda m: None)
        assert handler.name == "test"
        assert handler.priority == 100
        assert handler.only_guilds is True
        assert handler.ignore_bots is True
        assert handler.channel_whitelist is None
        assert handler.kwargs == {}

    def test_custom_values(self) -> None:
        async def dummy(m: object) -> None: ...

        handler = MessageHandler(
            name="custom",
            callback=dummy,
            priority=10,
            only_guilds=False,
            ignore_bots=False,
            channel_whitelist={1, 2, 3},
            kwargs={"foo": "bar"},
        )
        assert handler.priority == 10
        assert handler.only_guilds is False
        assert handler.ignore_bots is False
        assert handler.channel_whitelist == {1, 2, 3}
        assert handler.kwargs == {"foo": "bar"}
        assert handler.callback is dummy


# ------------------------------------------------------------------
# HandlerRegistry
# ------------------------------------------------------------------


class TestHandlerRegistry:
    """Tests for the HandlerRegistry class."""

    def test_empty_registry(self, fresh_registry: HandlerRegistry) -> None:
        assert fresh_registry.count == 0
        guild_mock = MagicMock()
        msg = _make_message(guild=guild_mock)
        assert fresh_registry.get_handlers(msg) == []

    def test_register_single(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        h = MessageHandler(name="h1", callback=handler)
        fresh_registry.register(h)
        assert fresh_registry.count == 1

    def test_register_multiple(self, fresh_registry: HandlerRegistry) -> None:
        async def h1(m: object) -> None: ...
        async def h2(m: object) -> None: ...

        fresh_registry.register_multiple(
            [
                MessageHandler(name="h1", callback=h1),
                MessageHandler(name="h2", callback=h2),
            ]
        )
        assert fresh_registry.count == 2

    def test_get_handlers_sorted_by_priority(self, fresh_registry: HandlerRegistry) -> None:
        async def low(m: object) -> None: ...
        async def high(m: object) -> None: ...

        fresh_registry.register(MessageHandler(name="high", callback=high, priority=50))
        fresh_registry.register(MessageHandler(name="low", callback=low, priority=200))
        guild = MagicMock()
        msg = _make_message(guild=guild)
        handlers = fresh_registry.get_handlers(msg)
        assert len(handlers) == 2
        assert handlers[0].name == "high"
        assert handlers[1].name == "low"

    # ------------------------------------------------------------------
    # Filter: ignore_bots
    # ------------------------------------------------------------------

    def test_ignore_bots_true_skips_bot_message(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(MessageHandler(name="h", callback=handler, ignore_bots=True))
        guild = MagicMock()
        msg = _make_message(author_bot=True, guild=guild)
        assert fresh_registry.get_handlers(msg) == []

    def test_ignore_bots_false_allows_bot(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(MessageHandler(name="h", callback=handler, ignore_bots=False))
        guild = MagicMock()
        msg = _make_message(author_bot=True, guild=guild)
        assert len(fresh_registry.get_handlers(msg)) == 1

    # ------------------------------------------------------------------
    # Filter: only_guilds
    # ------------------------------------------------------------------

    def test_only_guilds_true_skips_dm(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(MessageHandler(name="h", callback=handler, only_guilds=True))
        msg = _make_message(guild=None)  # DM
        assert fresh_registry.get_handlers(msg) == []

    def test_only_guilds_false_allows_dm(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(MessageHandler(name="h", callback=handler, only_guilds=False))
        msg = _make_message(guild=None)
        assert len(fresh_registry.get_handlers(msg)) == 1

    # ------------------------------------------------------------------
    # Filter: channel_whitelist
    # ------------------------------------------------------------------

    def test_channel_whitelist_matches(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(MessageHandler(name="h", callback=handler, channel_whitelist={100, 200}))
        guild = MagicMock()
        msg = _make_message(guild=guild, channel_id=100)
        assert len(fresh_registry.get_handlers(msg)) == 1

    def test_channel_whitelist_blocks(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(MessageHandler(name="h", callback=handler, channel_whitelist={200}))
        guild = MagicMock()
        msg = _make_message(guild=guild, channel_id=100)
        assert fresh_registry.get_handlers(msg) == []

    # ------------------------------------------------------------------
    # Combined filters
    # ------------------------------------------------------------------

    def test_combined_filters_all_pass(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(
            MessageHandler(
                name="h",
                callback=handler,
                only_guilds=True,
                ignore_bots=True,
                channel_whitelist={100},
            )
        )
        guild = MagicMock()
        msg = _make_message(guild=guild, channel_id=100)
        assert len(fresh_registry.get_handlers(msg)) == 1

    def test_combined_filters_one_fails(self, fresh_registry: HandlerRegistry) -> None:
        async def handler(m: object) -> None: ...

        fresh_registry.register(
            MessageHandler(
                name="h",
                callback=handler,
                only_guilds=True,
                ignore_bots=True,
                channel_whitelist={100},
            )
        )
        # Bot message in wrong channel
        guild = MagicMock()
        msg = _make_message(author_bot=True, guild=guild, channel_id=100)
        assert fresh_registry.get_handlers(msg) == []

        msg2 = _make_message(guild=guild, channel_id=999)
        assert fresh_registry.get_handlers(msg2) == []


# ------------------------------------------------------------------
# Convenience decorator: register_handler
# ------------------------------------------------------------------


class TestRegisterHandlerDecorator:
    """Tests for the @register_handler decorator."""

    def test_decorator_registers_handler(self) -> None:
        initial_count = _global_registry.count

        @register_handler()
        async def my_handler(m: object) -> None: ...

        assert _global_registry.count == initial_count + 1
        guild = MagicMock()
        msg = _make_message(guild=guild)
        handlers = _global_registry.get_handlers(msg)
        # Find the handler we just registered
        registered = [h for h in handlers if h.name == "my_handler"]
        assert len(registered) == 1
        assert registered[0].callback is my_handler

        # Clean up
        _global_registry._handlers = [h for h in _global_registry._handlers if h.name != "my_handler"]

    def test_decorator_custom_name(self) -> None:
        initial_count = _global_registry.count

        @register_handler(name="custom_name", priority=5)
        async def my_handler(m: object) -> None: ...

        assert _global_registry.count == initial_count + 1
        guild = MagicMock()
        msg = _make_message(guild=guild)
        handlers = _global_registry.get_handlers(msg)
        # Find the handler we just registered
        registered = [h for h in handlers if h.name == "custom_name"]
        assert len(registered) == 1
        assert registered[0].name == "custom_name"
        assert registered[0].priority == 5

        # Clean up
        _global_registry._handlers = [h for h in _global_registry._handlers if h.name != "custom_name"]

    def test_decorator_with_kwargs(self) -> None:
        initial_count = _global_registry.count

        @register_handler(name="test_kwargs", extra="value")
        async def my_handler(m: object, **kw: object) -> None: ...

        assert _global_registry.count == initial_count + 1
        # Find the handler we just registered
        registered = [h for h in _global_registry._handlers if h.name == "test_kwargs"]
        assert len(registered) == 1
        assert registered[0].kwargs == {"extra": "value"}

        # Clean up
        _global_registry._handlers = [h for h in _global_registry._handlers if h.name != "test_kwargs"]


# ------------------------------------------------------------------
# Singleton registry
# ------------------------------------------------------------------


class TestGlobalRegistry:
    """The module-level singleton exists and is usable."""

    def test_global_registry_is_instance(self) -> None:
        assert isinstance(_global_registry, HandlerRegistry)

    def test_global_registry_can_register(self) -> None:
        async def handler(m: object) -> None: ...

        try:
            _global_registry.register(
                MessageHandler(
                    name="_test_global",
                    callback=handler,
                    only_guilds=True,
                    ignore_bots=True,
                )
            )
            found = [h for h in _global_registry._handlers if h.name == "_test_global"]
            assert len(found) == 1
        finally:
            # Clean up so we don't pollute other tests
            _global_registry._handlers = [h for h in _global_registry._handlers if h.name != "_test_global"]

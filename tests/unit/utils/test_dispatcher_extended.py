from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from utils.dispatcher import (
    Priority,
    clear,
    dispatch,
    freeze,
    register,
    run_handlers_safe,
    run_handlers_sequential,
)


@pytest.fixture(autouse=True)
def reset_registry() -> None:
    clear()
    yield
    clear()


@pytest.mark.asyncio
async def test_register_decorator_form() -> None:
    @register(priority=Priority.HIGH)
    async def decorated_handler(_m: object) -> str:
        return "ok"

    message = MagicMock()
    message.author = MagicMock(bot=False)
    message.guild = MagicMock()
    message.channel = MagicMock(id=1)
    message.id = 1
    results = await dispatch(message)
    assert any(r == "ok" for _, r in results)


@pytest.mark.asyncio
async def test_register_after_freeze_raises() -> None:
    freeze()

    async def late(_m: object) -> None:
        pass

    with pytest.raises(RuntimeError):
        register(late)


@pytest.mark.asyncio
async def test_run_handlers_safe_exception_logged() -> None:
    message = MagicMock()
    message.id = 1
    message.channel = MagicMock(id=2)

    async def failing(*_a, **_k) -> None:
        raise ValueError("fail")

    handlers = [("fail", failing, (), {})]
    results = await run_handlers_safe(handlers, message)
    assert isinstance(results[0], ValueError)


@pytest.mark.asyncio
async def test_run_handlers_sequential_multiple() -> None:
    message = MagicMock()
    message.id = 1
    message.channel = MagicMock(id=2)
    calls: list[str] = []

    async def first(*_a, **_k) -> None:
        calls.append("first")

    async def second(*_a, **_k) -> None:
        calls.append("second")

    handlers = [("a", first, (), {}), ("b", second, (), {})]
    await run_handlers_sequential(handlers, message)
    assert calls == ["first", "second"]


@pytest.mark.asyncio
async def test_run_handlers_sequential_exception() -> None:
    message = MagicMock()
    message.id = 1
    message.channel = MagicMock(id=2)

    async def boom(*_a, **_k) -> None:
        raise RuntimeError("boom")

    results = await run_handlers_sequential([("x", boom, (), {})], message)
    assert isinstance(results[0], RuntimeError)


def test_freeze_sets_ready() -> None:
    freeze()
    with pytest.raises(RuntimeError):
        register(lambda _m: None)

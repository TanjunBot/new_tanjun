from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from diagnostics.infra_checks import check_database, check_gateway_latency, check_ping


@pytest.mark.asyncio
async def test_check_ping_ok() -> None:
    ctx = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    ctx.send = AsyncMock(return_value=msg)
    outcome = await check_ping(ctx, latency_limit_ms=5000)
    assert outcome.passed


@pytest.mark.asyncio
async def test_check_ping_too_slow() -> None:
    ctx = MagicMock()
    msg = MagicMock()
    msg.edit = AsyncMock()
    ctx.send = AsyncMock(return_value=msg)
    with patch("diagnostics.infra_checks.time.monotonic", side_effect=[0.0, 10.0]):
        outcome = await check_ping(ctx, latency_limit_ms=100)
    assert not outcome.passed


def test_check_gateway_latency_ok() -> None:
    bot = MagicMock()
    bot.latency = 0.05
    bot.shards = {}
    assert check_gateway_latency(bot, limit_ms=1000).passed


def test_check_gateway_latency_too_high() -> None:
    bot = MagicMock()
    bot.latency = 5.0
    assert not check_gateway_latency(bot, limit_ms=100).passed


@pytest.mark.asyncio
async def test_check_database_no_pool() -> None:
    bot = MagicMock(spec=[])
    assert not (await check_database(bot)).passed

from __future__ import annotations

import socket
from unittest.mock import MagicMock, patch

import pytest
from aiohttp import ClientSession

from extensions.prometheus_metrics import PrometheusMetricsCog
from services.metrics_service import command_usage
from tests.helpers.extension_loader import load_extension, make_bot_for_extensions

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.prometheus_metrics"

EXPECTED_METRIC_NAMES = (
    "tanjun_bot_tanjun_guild_count",
    "tanjun_commands_tanjun_command_usage_total",
    "tanjun_bot_tanjun_bot_start_time_seconds",
    "tanjun_system_tanjun_process_memory_bytes",
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture
def metrics_port() -> int:
    return _free_port()


async def _load_metrics_cog(bot: MagicMock, metrics_port: int) -> PrometheusMetricsCog:
    bot.guilds = []
    bot.users = []
    bot.shards = {}
    with patch("extensions.prometheus_metrics.metrics_port", metrics_port):
        await load_extension(bot, EXTENSION)
        cog: PrometheusMetricsCog = bot.cogs["PrometheusMetricsCog"]
        await cog.cog_load()
    return cog


async def test_setup_loads_prometheus_cog(metrics_port: int) -> None:
    bot = make_bot_for_extensions()
    with patch("extensions.prometheus_metrics.metrics_port", metrics_port):
        await load_extension(bot, EXTENSION)
    assert "PrometheusMetricsCog" in bot.cogs


async def test_metrics_endpoint_returns_expected_names(metrics_port: int) -> None:
    bot = make_bot_for_extensions()
    cog = await _load_metrics_cog(bot, metrics_port)
    try:
        async with ClientSession() as session:
            async with session.get(f"http://127.0.0.1:{metrics_port}/metrics") as resp:
                assert resp.status == 200
                body = await resp.text()
        for name in EXPECTED_METRIC_NAMES:
            assert name in body
    finally:
        await cog.cog_unload()


async def test_command_completion_increments_counter(metrics_port: int) -> None:
    bot = make_bot_for_extensions()
    cog = await _load_metrics_cog(bot, metrics_port)
    try:
        before = command_usage.labels(
            command="test_ping",
            guild_id="999",
            status="success",
        )._value.get()
        ctx = MagicMock()
        ctx.command = MagicMock()
        ctx.command.qualified_name = "test_ping"
        ctx.guild = MagicMock()
        ctx.guild.id = 999
        await cog.on_command_completion(ctx)
        after = command_usage.labels(
            command="test_ping",
            guild_id="999",
            status="success",
        )._value.get()
        assert after == before + 1

        async with ClientSession() as session:
            async with session.get(f"http://127.0.0.1:{metrics_port}/metrics") as resp:
                body = await resp.text()
        assert 'command="test_ping"' in body
        assert 'guild_id="999"' in body
    finally:
        await cog.cog_unload()


async def test_cog_unload_cleans_up_http_runner(metrics_port: int) -> None:
    bot = make_bot_for_extensions()
    cog = await _load_metrics_cog(bot, metrics_port)
    assert cog._runner is not None
    assert cog._site is not None
    await cog.cog_unload()
    assert cog._runner is None
    assert cog._site is None

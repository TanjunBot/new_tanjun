from __future__ import annotations

import time
from typing import Any

from diagnostics.models import CheckOutcome


async def check_ping(ctx: Any, latency_limit_ms: float = 5000) -> CheckOutcome:
    start = time.monotonic()
    msg = await ctx.send("ping")
    end = time.monotonic()
    latency = round((end - start) * 1000, 2)
    await msg.edit(content=f"Pong! ({latency}ms)")
    if latency > latency_limit_ms:
        return CheckOutcome("infra.ping", False, f"Ping latency too high: {latency}ms")
    return CheckOutcome("infra.ping", True, f"Pong! ({latency}ms)")


def check_gateway_latency(bot: Any, *, limit_ms: float = 1000.0) -> CheckOutcome:
    latency = getattr(bot, "latency", None)
    if latency is None:
        return CheckOutcome("infra.gateway_latency", False, "bot.latency unavailable")
    ms = round(latency * 1000, 2)
    if ms > limit_ms:
        return CheckOutcome("infra.gateway_latency", False, f"Gateway latency too high: {ms}ms")
    shard_count = len(getattr(bot, "shards", {}) or {})
    detail = f"{ms}ms"
    if shard_count:
        detail += f", shards={shard_count}"
    return CheckOutcome("infra.gateway_latency", True, detail)


async def check_database(bot: Any) -> CheckOutcome:
    pool = getattr(bot, "_pool", None)
    if pool is None:
        return CheckOutcome("infra.database", False, "Database pool not initialized on bot")
    try:
        async with pool.acquire() as conn, conn.cursor() as cursor:
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
        if not result or result[0] != 1:
            return CheckOutcome("infra.database", False, f"Unexpected result: {result}")
    except Exception as exc:
        return CheckOutcome("infra.database", False, str(exc))
    return CheckOutcome("infra.database", True, "Database connection verified")

from __future__ import annotations

import time
from typing import Any

from diagnostics.models import CheckOutcome


async def check_ping(ctx: Any, latency_limit_ms: float = 5000) -> CheckOutcome:
    start = time.time()
    msg = await ctx.send("ping")
    end = time.time()
    latency = round((end - start) * 1000, 2)
    await msg.edit(content=f"Pong! ({latency}ms)")
    if latency > latency_limit_ms:
        return CheckOutcome("infra.ping", False, f"Ping latency too high: {latency}ms")
    return CheckOutcome("infra.ping", True, f"Pong! ({latency}ms)")


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

"""Ping test for the test_bot admin command."""

import time

from discord.ext import commands

__test__ = False


async def test_ping(self: commands.Cog, ctx: commands.Context) -> None:
    """Verify the bot responds to a basic ping."""
    start = time.time()
    msg = await ctx.send("ping")
    end = time.time()
    latency = round((end - start) * 1000, 2)
    await msg.edit(content=f"Pong! ({latency}ms)")
    if latency > 5000:
        raise TimeoutError(f"Ping latency too high: {latency}ms")

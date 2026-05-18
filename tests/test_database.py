"""Database connectivity test for the test_bot admin command.

Called by extensions/administration.py test_bot command.
Tests basic database connectivity using the bot's connection pool.
"""

import discord
from discord.ext import commands

__test__ = False


async def test_database(self: commands.Cog, ctx: commands.Context) -> None:  # type: ignore[type-arg]
    """Verify the bot can query the database."""
    pool = getattr(ctx.bot, "_pool", None)
    if pool is None:
        raise ConnectionError("Database pool not initialized on bot")

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            if not result or result[0] != 1:
                raise AssertionError(f"Database ping returned unexpected result: {result}")

    await ctx.send("✅ Database connection verified")

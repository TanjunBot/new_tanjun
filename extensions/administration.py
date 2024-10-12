"""
THE COMMANDS IN THIS FILE ARE FOR ADMINISTRATIVE PURPOSES ONLY. THEY ARE NOT TO BE SHARED WITH ANYONE ELSE!
"""

import asyncio
import discord
from discord.ext import commands
import config
from utility import addFeedback
from tests import (
    test_ping,
    test_database,
    test_commands,
)


class administrationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx) -> None:
        if ctx.author.id not in config.adminIds:
            return
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"{len(fmt)} Befehle wurden gesynced.")

    @commands.command()
    async def feedback(self, ctx, *, content) -> None:
        if ctx.author.id not in [
            689755528947433555,
            892113092387942420,
            806086469268668437,
        ]:
            return
        addFeedback(content, ctx.author.name)
        await ctx.send("Feedback wurde hinzugefügt. Vielen dank!")

    @commands.command()
    async def test_bot(self, ctx):
        if ctx.author.id not in config.adminIds:
            return

        message = await ctx.send("Starting bot tests...")

        await message.edit(content="Starting bot tests... \ncurrent Test: `Ping`")
        try:
            await test_ping(self, ctx)
        except Exception as e:
            await message.edit(content=f"❌ Error in Ping test: {e}")
            return
        await message.edit(
            content="Starting bot tests... \nPing Test: ✅\ncurrent Test: `Database`"
        )
        try:
            await test_database(self, ctx)
        except Exception as e:
            await message.edit(content=f"❌ Error in Database test: {e}")
            return
        await message.edit(
            content="Starting bot tests... \nPing Test: ✅\nDatabase Test: ✅\ncurrent Test: `Commands`"
        )
        try:
            await test_commands(self, ctx)
        except Exception as e:
            raise
            await message.edit(content=f"❌ Error in Commands test: {e}")
            return
        await message.edit(
            content="Starting bot tests... \nPing Test: ✅\nDatabase Test: ✅\nCommands Test: ✅\nAll tests completed successfully. The bot seems to be working fine."
        )


async def setup(bot):
    await bot.add_cog(administrationCog(bot))

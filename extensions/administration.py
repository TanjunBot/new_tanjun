"""
THE COMMANDS IN THIS FILE ARE FOR ADMINISTRATIVE PURPOSES ONLY. THEY ARE NOT TO BE SHARED WITH ANYONE ELSE!
"""

import asyncio
import discord
from discord.ext import commands
from localizer import tanjunLocalizer
import config
from utility import addFeedback
from api import feedbackBlockUser, feedbackUnblockUser
from tests import (
    test_ping,
    test_database,
    test_commands,
)
import subprocess
import platform


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
    async def blockFeedback(self, ctx, user: discord.User) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await feedbackBlockUser(user.id)
        await ctx.send(f"{user.name} wurde blockiert.")

    @commands.command()
    async def unblockFeedback(self, ctx, user: discord.User) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await feedbackUnblockUser(user.id)
        await ctx.send(f"{user.name} wurde entblockiert.")

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
            await message.edit(content=f"❌ Error in Commands test: {e}")
            return
        await message.edit(
            content="Starting bot tests... \nPing Test: ✅\nDatabase Test: ✅\nCommands Test: ✅\nAll tests completed successfully. The bot seems to be working fine."
        )

    @commands.command()
    async def test_translation(self, ctx):
        if ctx.author.id not in config.adminIds:
            return
        text = tanjunLocalizer.test_localize("de", "commands.logs")
        await ctx.send(str(text)[:4000])

    @commands.command()
    async def update(self, ctx):
        print(config.adminIds)
        if ctx.author.id not in config.adminIds:
            return

        sh_file = "update.sh"
        if platform.system() == "Windows":
            await ctx.send(
                "Bot is Updating... Please note that this might not work on Windows. If it does, please let me know :) I might die during this process :("
            )
            sh_file = "update.bat"
            result = subprocess.run(
                [sh_file], capture_output=True, text=True, check=True
            )
            await ctx.send(result.stdout)
            return

        await ctx.send(
            "Updating... Please check again in a few seconds if im still alive. I may die during this process :("
        )
        result = subprocess.run(
            ["bash", sh_file], capture_output=True, text=True, check=True
        )
        await ctx.send(result.stdout)


async def setup(bot):
    await bot.add_cog(administrationCog(bot))

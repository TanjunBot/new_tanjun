"""
THE COMMANDS IN THIS FILE ARE FOR ADMINISTRATIVE PURPOSES ONLY. THEY ARE NOT TO BE SHARED WITH ANYONE ELSE!
"""

# Unused imports:
# import asyncio
# import subprocess
# import platform
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
from extensions.logs import sendLogEmbeds
from loops.create_database_backup import create_database_backup
from commands.admin.joinToCreate.joinToCreateListener import removeAllJoinToCreateChannels
import aiohttp
from commands.admin.channel.welcome import welcomeNewUser

from commands.admin.channel.farewell import farewellUser


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

        await sendLogEmbeds(self.bot)
        await create_database_backup(self.bot)
        await removeAllJoinToCreateChannels()
        await ctx.send("Updating...")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://127.0.0.1:6969/restart/{self.bot.application_id}"
            ) as response:
                await ctx.send(await response.text())

    @commands.command()
    async def welcome(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if ctx.author.id not in config.adminIds:
            return
        await welcomeNewUser(user)

    @commands.command()
    async def farewell(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if ctx.author.id not in config.adminIds:
            return
        await farewellUser(user)


async def setup(bot):
    await bot.add_cog(administrationCog(bot))

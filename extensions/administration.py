"""
THE COMMANDS IN THIS FILE ARE FOR ADMINISTRATIVE PURPOSES ONLY. THEY ARE NOT TO BE SHARED WITH ANYONE ELSE!
"""
import asyncio
import signal
import discord
from discord.ext import commands
import time
import config
from utility import addFeedback
from api import feedbackBlockUser, feedbackUnblockUser

class administrationCog(commands.Cog):
    @commands.command()
    async def sync(self, ctx) -> None:
        if ctx.author.id not in config.adminIds:
            return
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"{len(fmt)} Befehle wurden gesynced.")

    @commands.command()
    async def feedback(self, ctx, *, content) -> None:
        if ctx.author.id not in [689755528947433555, 892113092387942420, 806086469268668437]:
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

async def setup(bot):
    await bot.add_cog(administrationCog(bot))
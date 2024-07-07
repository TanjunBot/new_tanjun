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

class administrationCog(commands.Cog):
    @commands.command()
    async def sync(self, ctx) -> None:
        if ctx.author.id not in config.adminIds:
            return
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"{len(fmt)} Befehle wurden gesynced.")

    @commands.command()
    async def feedback(self, ctx, *, content) -> None:
        if ctx.author.id not in [689755528947433555, 892113092387942420]:
            return
        addFeedback(content, ctx.author.name)
        await ctx.send("Feedback wurde hinzugefügt. Vielen dank!")

async def setup(bot):
    await bot.add_cog(administrationCog(bot))
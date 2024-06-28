import discord
from discord.ext import commands, tasks
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from loops.giveaway import sendReadyGiveaways

class LoopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=10)
    async def sendSendReadyGiveaways(self):
        try:
            await sendReadyGiveaways(self.bot)
        except:
            pass

    @commands.Cog.listener()
    async def on_ready(self):  
        self.sendSendReadyGiveaways.start()


async def setup(bot):
    await bot.add_cog(LoopCog(bot))

import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List, Optional

from minigames.counting import counting
from minigames.countingChallenge import counting as countingChallenge
from minigames.countingmodes import counting as countingModes

class ListenerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await counting(message)
        await countingChallenge(message)
        await countingModes(message)

async def setup(bot):
    await bot.add_cog(ListenerCog(bot))

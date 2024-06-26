import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List, Optional

from minigames import counting

class ListenerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await counting(message)

async def setup(bot):
    await bot.add_cog(ListenerCog(bot))

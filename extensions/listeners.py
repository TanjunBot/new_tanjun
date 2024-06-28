import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List, Optional

from minigames.counting import counting
from minigames.countingChallenge import counting as countingChallenge
from minigames.countingmodes import counting as countingModes
from minigames.wordchain import wordchain
from minigames.addLevelXp import addLevelXp

from commands.giveaway.utility import add_giveaway_participant

class ListenerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await counting(message)
        await countingChallenge(message)
        await countingModes(message)
        await wordchain(message)
        await addLevelXp(message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.data["custom_id"].startswith("giveaway_enter"):
            giveaway_id = interaction.data["custom_id"].split("; ")[1]
            embed = await add_giveaway_participant(giveawayid=giveaway_id, userid=interaction.user.id, client=self.bot)
            print("embed: ", embed)
            if embed:
                await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ListenerCog(bot))

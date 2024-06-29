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

from commands.giveaway.utility import add_giveaway_participant, addMessageToGiveaway
from loops.level import handleVoiceChange as handleLevelVoiceChange
from loops.giveaway import handleVoiceChange

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
        await addMessageToGiveaway(message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            if interaction.data["custom_id"].startswith("giveaway_enter"):
                giveaway_id = interaction.data["custom_id"].split("; ")[1]
                embed = await add_giveaway_participant(giveawayid=giveaway_id, userid=interaction.user.id, client=self.bot)
                if embed:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        await handleVoiceChange(user, before, after)
        await handleLevelVoiceChange(user, before, after)

async def setup(bot):
    await bot.add_cog(ListenerCog(bot))

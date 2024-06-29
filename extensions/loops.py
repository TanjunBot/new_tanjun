import discord
from discord.ext import commands, tasks
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from loops.giveaway import sendReadyGiveaways
from loops.giveaway import checkVoiceUsers
from loops.giveaway import endGiveaways
from minigames.addLevelXp import clearNotifiedUsers
from loops.level import addXpToVoiceUsers

class LoopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=10)
    async def sendSendReadyGiveaways(self):
        try:
            await sendReadyGiveaways(self.bot)
        except:
            pass
    
    @tasks.loop(seconds=10)
    async def endGiveawaysLoop(self):
        try:
            await endGiveaways(self.bot)
        except:
            pass

    @tasks.loop(seconds=60)
    async def checkVoiceUsers(self):
        try:
            await checkVoiceUsers(self.bot)
        except:
            pass

    @tasks.loop(seconds=5)
    async def clearNotifiedUsersLoop(self):
        try:
            await clearNotifiedUsers(self.bot)
        except:
            pass

    @tasks.loop(seconds=5)
    async def addVoiceUserLoop(self):
        try:
            await addXpToVoiceUsers(self.bot)
        except:
            raise

    @commands.Cog.listener()
    async def on_ready(self):  
        self.sendSendReadyGiveaways.start()
        self.endGiveawaysLoop.start()
        self.checkVoiceUsers.start()
        self.clearNotifiedUsersLoop.start()
        self.addVoiceUserLoop.start()


async def setup(bot):
    await bot.add_cog(LoopCog(bot))

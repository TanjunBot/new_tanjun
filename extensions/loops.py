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
from ai.refillToken import refillAiToken
from loops.alivemonitor import ping_server
from loops.create_database_backup import create_database_backup
from extensions.logs import sendLogEmbeds
import asyncio

from api import check_pool_initialized

embeds = {}

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

    @tasks.loop(seconds=60)
    async def refillAiTokenLoop(self):
        try:
            await refillAiToken(self.bot)
        except:
            raise

    @tasks.loop(seconds=5)
    async def pingServerLoop(self):
        try:
            await ping_server(self.bot)
        except:
            raise

    @tasks.loop(hours=1)
    async def backupDatabaseLoop(self):
        try:
            await create_database_backup(self.bot)
        except:
            raise

    @tasks.loop(seconds=10)
    async def sendLogEmbeds(self):
        try:
            await sendLogEmbeds(self)
        except:
            raise
                

    @commands.Cog.listener()
    async def on_ready(self):  
        while not check_pool_initialized():
            await asyncio.sleep(1)
                    
            self.sendSendReadyGiveaways.start()
            self.endGiveawaysLoop.start()
            self.checkVoiceUsers.start()
            self.clearNotifiedUsersLoop.start()
            self.addVoiceUserLoop.start()
            self.refillAiTokenLoop.start()
            self.pingServerLoop.start()
            self.backupDatabaseLoop.start()
            self.sendLogEmbeds.start()



async def setup(bot):
    await bot.add_cog(LoopCog(bot))

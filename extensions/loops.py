# Unused imports:
# import discord
# import utility
# from discord import app_commands
# from localizer import tanjunLocalizer
from discord.ext import commands, tasks

from loops.giveaway import sendReadyGiveaways
from loops.giveaway import checkVoiceUsers
from loops.giveaway import endGiveaways
from minigames.addLevelXp import clearNotifiedUsers
from loops.level import addXpToVoiceUsers
from ai.refillToken import refillAiToken
from loops.alivemonitor import ping_server
from loops.create_database_backup import create_database_backup
from extensions.logs import sendLogEmbeds
from commands.utility.claimBoosterRole import remove_claimed_booster_roles_that_are_expired
from commands.utility.claimBoosterChannel import remove_claimed_booster_channels_that_are_expired
from commands.utility.schedulemessage import send_scheduled_messages
import asyncio

from api import check_pool_initialized, get_all_twitch_notification_uuids
from commands.utility.twitch.twitchApi import getTwitchApi, notify_twitch_online

embeds = {}


class LoopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=10)
    async def sendSendReadyGiveaways(self):
        try:
            await sendReadyGiveaways(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def endGiveawaysLoop(self):
        try:
            await endGiveaways(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=60)
    async def checkVoiceUsers(self):
        try:
            await checkVoiceUsers(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=5)
    async def clearNotifiedUsersLoop(self):
        try:
            await clearNotifiedUsers(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=5)
    async def addVoiceUserLoop(self):
        try:
            await addXpToVoiceUsers(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=60)
    async def refillAiTokenLoop(self):
        try:
            await refillAiToken(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=5)
    async def pingServerLoop(self):
        try:
            await ping_server(self.bot)
        except Exception:
            pass

    @tasks.loop(hours=1)
    async def backupDatabaseLoop(self):
        try:
            await create_database_backup(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def sendLogEmbeds(self):
        try:
            await sendLogEmbeds(self.bot)
        except Exception:
            raise

    @tasks.loop(seconds=10)
    async def removeExpiredClaimedBoosterRoles(self):
        try:
            await remove_claimed_booster_roles_that_are_expired(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def removeExpiredClaimedBoosterChannels(self):
        try:
            await remove_claimed_booster_channels_that_are_expired(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def sendScheduledMessages(self):
        try:
            await send_scheduled_messages(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def pollTwitchStreams(self):
        try:
            twitch_api = getTwitchApi()
            if not twitch_api:
                return

            uuids = await get_all_twitch_notification_uuids()
            if not uuids:
                return

            # Convert list of tuples to list of strings
            user_ids = [str(uuid[0]) for uuid in uuids]

            # Initialize stream status on first run
            if not twitch_api.initial_check_done:
                await twitch_api.initialize_stream_status(user_ids)
                return  # Skip notifications on first check

            streams = await twitch_api.get_streams(user_ids)
            live_streams = {stream["user_id"]: stream for stream in streams}

            # Check for newly live streams
            for uuid in user_ids:
                was_live = twitch_api.stream_status.get(uuid, False)
                is_live = uuid in live_streams

                if not was_live and is_live:
                    # Stream just went live
                    await notify_twitch_online(self.bot, uuid, live_streams[uuid])

                twitch_api.stream_status[uuid] = is_live

        except Exception:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        while not check_pool_initialized():
            await asyncio.sleep(1)

        self.pollTwitchStreams.start()
        self.sendSendReadyGiveaways.start()
        self.endGiveawaysLoop.start()
        self.checkVoiceUsers.start()
        self.clearNotifiedUsersLoop.start()
        self.addVoiceUserLoop.start()
        self.refillAiTokenLoop.start()
        self.pingServerLoop.start()
        self.backupDatabaseLoop.start()
        self.sendLogEmbeds.start()
        self.removeExpiredClaimedBoosterRoles.start()
        self.removeExpiredClaimedBoosterChannels.start()
        self.sendScheduledMessages.start()


async def setup(bot):
    await bot.add_cog(LoopCog(bot))

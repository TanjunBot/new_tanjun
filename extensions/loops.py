# Unused imports:
# import discord
# import utility
# from discord import app_commands
# from localizer import tanjunLocalizer
import asyncio
from datetime import time

import discord
from discord.ext import commands, tasks

from ai.refillToken import refillAiToken
from api import get_all_twitch_notification_uuids
from commands.utility.claimBoosterChannel import (
    remove_claimed_booster_channels_that_are_expired,
)
from commands.utility.claimBoosterRole import (
    remove_claimed_booster_roles_that_are_expired,
)
from commands.utility.schedulemessage import send_scheduled_messages
from commands.utility.twitch.twitchApi import getTwitchApi, notify_twitch_online
from loops.alivemonitor import ping_server
from loops.create_database_backup import create_database_backup
from loops.giveaway import checkVoiceUsers, endGiveaways, sendReadyGiveaways
from loops.level import addXpToVoiceUsers
from minigames.addLevelXp import clearNotifiedUsers

embeds = {}  # type: ignore[var-annotated]


class LoopCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @tasks.loop(seconds=10)
    async def sendSendReadyGiveaways(self) -> None:
        try:
            await sendReadyGiveaways(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def endGiveawaysLoop(self) -> None:
        try:
            await endGiveaways(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            pass

    @tasks.loop(seconds=60)
    async def checkVoiceUsers(self) -> None:
        try:
            await checkVoiceUsers(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            pass

    @tasks.loop(seconds=5)
    async def clearNotifiedUsersLoop(self) -> None:
        try:
            await clearNotifiedUsers(self.bot)  # type: ignore[misc, call-arg, func-returns-value]  # type: ignore[func-returns-value]  # type: ignore[func-returns-value]  # type: ignore[func-returns-value]
        except Exception:
            pass

    @tasks.loop(seconds=5)
    async def addVoiceUserLoop(self) -> None:
        try:
            await addXpToVoiceUsers(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            pass

    @tasks.loop(seconds=60)
    async def refillAiTokenLoop(self) -> None:
        try:
            await refillAiToken(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=5)
    async def pingServerLoop(self) -> None:
        try:
            await ping_server(self.bot)
        except Exception:
            pass

    @tasks.loop(hours=1)
    async def backupDatabaseLoop(self) -> None:
        try:
            await create_database_backup(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def removeExpiredClaimedBoosterRoles(self) -> None:
        try:
            await remove_claimed_booster_roles_that_are_expired(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def removeExpiredClaimedBoosterChannels(self) -> None:
        try:
            await remove_claimed_booster_channels_that_are_expired(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def sendScheduledMessages(self) -> None:
        try:
            await send_scheduled_messages(self.bot)
        except Exception:
            pass

    @tasks.loop(seconds=10)
    async def pollTwitchStreams(self) -> None:
        try:
            twitch_api = getTwitchApi()
            if not twitch_api:
                return

            uuids = await get_all_twitch_notification_uuids()
            if not uuids:
                return

            # uuids is already a list of strings
            user_ids = [str(uuid) for uuid in uuids]

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

    @tasks.loop(time=[time(hour=2), time(hour=8), time(hour=14), time(hour=20)])
    async def sendPokemonWerbung(self) -> None:
        try:
            message = """
👋 Heyo! 👋
Wir sind ein netter, aktiver und nicer Community-Server, der mit Pokémonfans bereichert ist! Man muss hier aber nicht unbedingt Pokémon gespielt haben oder gar kennen. Inzwischen haben wir uns zu einem relativ "normalen" Community-Server entwickelt, denn wir reden auch über viele andere Themen! Über alle, die uns eben einfallen! <:P_crazy_evoli:905008625892855820>
**Schau doch mal bei uns vorbei und mach dir selbst ein Bild! Wir würden uns freuen, wenn du joinst :D**

__Wir haben zum Beispiel:__
<:P_Meowwwwwwww:892120072666120192> | Nette & aktive Community
🎭 | Selfroles
🌹 | Keine @-everyone oder @-here Pings
📨 | Werbemöglichkeiten
📑 | Guter Support
<:P_SUPERFUNNYBREAD:867370461931372544> | Fun-Botbefehle
<:P_heart_boost:861209379998924800> | Viele Vorteile für Booster, Sponsoren & Co.
<:P_Pikaluv:847828564006010930> | Pokédexeinträge, Umfragen und mehr!
♥️ | Jede Menge Events & ähnliches Zeugs
🎁 | Giveaways :D
🌟 | Specialchats
<:P_bisasam_euh:870375183444230194> | Und vieles mehr!

Jede(r) ist ♥️-lich willkommen! Wir freuen uns über jeden Neuzugang! Schaut gern mal bei uns vorbei!

**➡️ Klick hier zum Joinen! ⬅️**
<https://discord.gg/D3UVPKseD8>
            """
            channel = self.bot.get_channel(923337160600477777)
            if isinstance(channel, discord.TextChannel):
                embed = discord.Embed(description=message, color=0xCB33F5, title="🐾Pokémon🐾")
                sent_message = await channel.send(embed=embed)
                if sent_message.guild:
                    await sent_message.publish()
        except Exception:
            raise

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # Wait until the database pool is initialized
        while not hasattr(self.bot, "_pool") or self.bot._pool is None:
            await asyncio.sleep(1)

        self.pollTwitchStreams.start()  # type: ignore[unused-awaitable]
        self.sendSendReadyGiveaways.start()  # type: ignore[unused-awaitable]
        self.endGiveawaysLoop.start()  # type: ignore[unused-awaitable]
        self.checkVoiceUsers.start()  # type: ignore[unused-awaitable]
        self.clearNotifiedUsersLoop.start()  # type: ignore[unused-awaitable]
        self.addVoiceUserLoop.start()  # type: ignore[unused-awaitable]
        self.refillAiTokenLoop.start()  # type: ignore[unused-awaitable]
        self.pingServerLoop.start()  # type: ignore[unused-awaitable]
        self.backupDatabaseLoop.start()  # type: ignore[unused-awaitable]
        self.removeExpiredClaimedBoosterRoles.start()  # type: ignore[unused-awaitable]
        self.removeExpiredClaimedBoosterChannels.start()  # type: ignore[unused-awaitable]
        self.sendScheduledMessages.start()  # type: ignore[unused-awaitable]
        self.sendPokemonWerbung.start()  # type: ignore[unused-awaitable]


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LoopCog(bot))

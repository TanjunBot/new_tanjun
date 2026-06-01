import asyncio
import logging
from datetime import time

import discord
from discord.ext import commands, tasks

from config import sentry_dsn

logger = logging.getLogger(__name__)


# ── Sentry helper ────────────────────────────────────────────────────────────
def _log_loop_error(task_name: str) -> None:
    """Log a background loop exception and report to Sentry (if configured)."""
    logger.exception("Error in loop task %s", task_name)
    if sentry_dsn:
        try:
            import sentry_sdk

            sentry_sdk.capture_exception(tags={"loop_task": task_name})
        except Exception:
            pass  # Don't let Sentry itself break the loop


from ai.refill_token import refill_ai_token
from commands.utility.claim_booster_channel import (
    remove_claimed_booster_channels_that_are_expired,
)
from commands.utility.claim_booster_role import (
    remove_claimed_booster_roles_that_are_expired,
)
from commands.utility.schedulemessage import send_scheduled_messages
from commands.utility.twitch.twitch_api import notify_twitch_online
from loops.alivemonitor import ping_server
from loops.create_database_backup import create_database_backup
from loops.giveaway import checkVoiceUsers, endGiveaways, sendReadyGiveaways
from loops.level import addXpToVoiceUsers
from minigames.add_level_xp import clearNotifiedUsers
from services.twitch_service import get_twitch_service
from utility import EmbedColor

embeds = {}  # type: ignore[var-annotated]


class LoopCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @tasks.loop(seconds=30)
    async def sendSendReadyGiveaways(self) -> None:
        try:
            await sendReadyGiveaways(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            _log_loop_error("sendSendReadyGiveaways")

    @tasks.loop(seconds=30)
    async def endGiveawaysLoop(self) -> None:
        try:
            await endGiveaways(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            _log_loop_error("endGiveawaysLoop")

    @tasks.loop(seconds=60)
    async def checkVoiceUsers(self) -> None:
        try:
            await checkVoiceUsers(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            _log_loop_error("checkVoiceUsers")

    @tasks.loop(seconds=60)
    async def clearNotifiedUsersLoop(self) -> None:
        try:
            clearNotifiedUsers(self.bot)
        except Exception:
            _log_loop_error("clearNotifiedUsersLoop")

    @tasks.loop(seconds=30)
    async def addVoiceUserLoop(self) -> None:
        try:
            await addXpToVoiceUsers(self.bot)  # type: ignore[no-untyped-call]
        except Exception:
            _log_loop_error("addVoiceUserLoop")

    @tasks.loop(seconds=60)
    async def refillAiTokenLoop(self) -> None:
        try:
            await refill_ai_token(self.bot)
        except Exception:
            _log_loop_error("refillAiTokenLoop")

    @tasks.loop(seconds=60)
    async def pingServerLoop(self) -> None:
        try:
            await ping_server(self.bot)
        except Exception:
            _log_loop_error("pingServerLoop")

    @tasks.loop(hours=1)
    async def backupDatabaseLoop(self) -> None:
        try:
            await create_database_backup(self.bot)
        except Exception:
            _log_loop_error("backupDatabaseLoop")

    @backupDatabaseLoop.before_loop
    async def before_backup_database(self) -> None:
        await asyncio.sleep(3600)

    @tasks.loop(seconds=30)
    async def removeExpiredClaimedBoosterRoles(self) -> None:
        try:
            await remove_claimed_booster_roles_that_are_expired(self.bot)
        except Exception:
            _log_loop_error("removeExpiredClaimedBoosterRoles")

    @tasks.loop(seconds=30)
    async def removeExpiredClaimedBoosterChannels(self) -> None:
        try:
            await remove_claimed_booster_channels_that_are_expired(self.bot)
        except Exception:
            _log_loop_error("removeExpiredClaimedBoosterChannels")

    @tasks.loop(seconds=30)
    async def sendScheduledMessages(self) -> None:
        try:
            await send_scheduled_messages(self.bot)
        except Exception:
            _log_loop_error("sendScheduledMessages")

    @tasks.loop(seconds=60)  # Twitch API rate limits
    async def pollTwitchStreams(self) -> None:
        try:
            twitch_service = get_twitch_service()
            if not twitch_service:
                return

            uuids = await twitch_service.get_all_notification_uuids()
            if not uuids:
                return

            # uuids is already a list of strings
            user_ids = [str(uuid) for uuid in uuids]

            # Initialize stream status on first run
            if not twitch_service.initial_check_done:
                await twitch_service.initialize_stream_status(user_ids)
                return  # Skip notifications on first check

            streams = await twitch_service.get_streams(user_ids)
            live_streams = {stream["user_id"]: stream for stream in streams}

            # Batch notification for streams going live simultaneously
            newly_live = [
                uuid for uuid in user_ids if not twitch_service.stream_status.get(uuid, False) and uuid in live_streams
            ]

            if newly_live:
                await asyncio.gather(
                    *(notify_twitch_online(self.bot, uuid, live_streams[uuid]) for uuid in newly_live),
                    return_exceptions=True,
                )

            # Update status for all tracked uuids
            for uuid in user_ids:
                twitch_service.stream_status[uuid] = uuid in live_streams

        except Exception:
            _log_loop_error("pollTwitchStreams")

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
                embed = discord.Embed(description=message, color=EmbedColor.BRAND.value, title="🐾Pokémon🐾")
                sent_message = await channel.send(embed=embed)
                if sent_message.guild:
                    await sent_message.publish()
        except Exception:
            _log_loop_error("sendPokemonWerbung")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # Wait until the database pool is initialized (signaled via Event)
        if not hasattr(self.bot, "_pool_ready"):
            self.bot._pool_ready = asyncio.Event()
        await self.bot._pool_ready.wait()

        loop_starts = [
            self.pollTwitchStreams,
            self.sendSendReadyGiveaways,
            self.endGiveawaysLoop,
            self.checkVoiceUsers,
            self.clearNotifiedUsersLoop,
            self.addVoiceUserLoop,
            self.refillAiTokenLoop,
            self.pingServerLoop,
            self.backupDatabaseLoop,
            self.removeExpiredClaimedBoosterRoles,
            self.removeExpiredClaimedBoosterChannels,
            self.sendScheduledMessages,
            self.sendPokemonWerbung,
        ]
        for loop in loop_starts:
            if not loop.is_running():
                loop.start()  # type: ignore[unused-awaitable]
            await asyncio.sleep(0.25)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LoopCog(bot))

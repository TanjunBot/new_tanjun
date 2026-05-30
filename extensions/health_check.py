from typing import Any

from health.checks import HealthCheck, HealthCheckResult, HealthStatus


class BackgroundLoopHealthCheck(HealthCheck):
    """Health check for background task loops.

    The bot relies on multiple background task loops (extensions/loops.py):
    - Giveaway sending (10s)
    - Giveaway ending (10s)
    - Voice checking (60s)
    - Voice XP processing (5s)
    - AI token refill (60s)
    - Server pinging (5s)
    - Database backup (1h)
    - Booster role/channel cleanup (10s)
    - Scheduled messages (10s)
    - Twitch polling (10s)
    - Clear Notified Users (5s)
    - Pokemon Werbung (scheduled: 2am, 8am, 2pm, 8pm)

    If one of these loops stops unexpectedly, the feature stops working.
    Most loops log exceptions and continue; this check detects stopped tasks.
    """

    def __init__(self, bot: Any):
        self.bot = bot

    @property
    def name(self) -> str:
        return "Background Loops"

    @property
    def critical(self) -> bool:
        return True  # Missing LoopCog is critical

    async def run(self) -> HealthCheckResult:
        cog = self.bot.get_cog("LoopCog")
        if not cog:
            return HealthCheckResult(
                self.name,
                HealthStatus.CRITICAL,
                "LoopCog not found. No background tasks registered.",
            )

        # Check each loop task (use safe attribute resolution)
        loop_specs = [
            ("Giveaway Sender", "sendSendReadyGiveaways"),
            ("Giveaway Ender", "endGiveawaysLoop"),
            ("Voice Checker", "checkVoiceUsers"),
            ("Voice XP", "addVoiceUserLoop"),
            ("AI Token Refill", "refillAiTokenLoop"),
            ("Ping Server", "pingServerLoop"),
            ("Database Backup", "backupDatabaseLoop"),
            ("Booster Roles", "removeExpiredClaimedBoosterRoles"),
            ("Booster Channels", "removeExpiredClaimedBoosterChannels"),
            ("Scheduled Messages", "sendScheduledMessages"),
            ("Twitch Polling", "pollTwitchStreams"),
            ("Clear Notified Users", "clearNotifiedUsersLoop"),
            ("Pokemon Werbung", "sendPokemonWerbung"),
        ]

        failed_loops = []
        for name, attr in loop_specs:
            task = getattr(cog, attr, None)
            if task is None:
                failed_loops.append(f"{name} (missing)")
                continue
            try:
                is_running = task.is_running
            except AttributeError:
                failed_loops.append(f"{name} (invalid)")
                continue
            if not callable(is_running):
                failed_loops.append(f"{name} (invalid)")
                continue
            try:
                if not is_running():
                    failed_loops.append(name)
            except AttributeError:
                failed_loops.append(f"{name} (error)")

        if failed_loops:
            return HealthCheckResult(
                self.name,
                HealthStatus.DEGRADED,
                f"Failed loops: {', '.join(failed_loops)}",
                details={"failed_loops": failed_loops},
            )

        return HealthCheckResult(
            self.name,
            HealthStatus.HEALTHY,
            f"All {len(loop_specs)} background loops are running.",
        )

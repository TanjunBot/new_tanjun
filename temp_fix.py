class BackgroundLoopHealthCheck(HealthCheck):
    def __init__(self, bot):
        self.bot = bot
    
    @property
    def name(self) -> str:
        return "Background Loops"
    
    @property
    def critical(self) -> bool:
        return False  # Individual loops failing is degraded, not critical
    
    async def run(self) -> HealthCheckResult:
        cog = self.bot.get_cog("LoopCog")
        if not cog:
            return HealthCheckResult(
                self.name, HealthStatus.CRITICAL,
                "LoopCog not found. No background tasks registered.",
            )
        
        loop_tasks = [
            ("Giveaway Sender", cog.sendSendReadyGiveaways),
            ("Giveaway Ender", cog.endGiveawaysLoop),
            ("Voice Checker", cog.checkVoiceUsers),
            ("Voice XP", cog.addVoiceUserLoop),
            ("AI Token Refill", cog.refillAiTokenLoop),
            ("Ping Server", cog.pingServerLoop),
            ("Database Backup", cog.backupDatabaseLoop),
            ("Booster Roles", cog.removeExpiredClaimedBoosterRoles),
            ("Booster Channels", cog.removeExpiredClaimedBoosterChannels),
            ("Scheduled Messages", cog.sendScheduledMessages),
            ("Twitch Polling", cog.pollTwitchStreams),
        ]
        
        failed_loops = []
        for name, task in loop_tasks:
            if not task.is_running():
                failed_loops.append(name)
        
        if failed_loops:
            return HealthCheckResult(
                self.name, HealthStatus.DEGRADED,
                f"Stopped loops: {', '.join(failed_loops)}",
                details={"stopped_loops": failed_loops},
            )
        
        return HealthCheckResult(
            self.name, HealthStatus.HEALTHY,
            f"All {len(loop_tasks)} background loops are running.",
        )
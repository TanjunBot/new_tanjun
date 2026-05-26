# Background Loop Health Check

Requires the HealthCheck framework from the main health check issue.

The bot relies on multiple background task loops (`extensions/loops.py`):
- Giveaway sending (10s)
- Giveaway ending (10s)
- Voice XP processing (5s)
- AI token refill (60s)
- Server pinging (5s)
- Database backup (1h)
- Booster role/channel cleanup (10s)
- Scheduled messages (10s)
- Twitch polling (10s)

If one of these loops crashes silently (they all use `except Exception: pass`), the feature stops working without any notification.

## Implementation

```python
class BackgroundLoopHealthCheck(HealthCheck):
    def __init__(self, bot):
        self.bot = bot
    
    @property
    def name(self) -> str: return "Background Loops"
    @property
    def critical(self) -> bool: return False  # Individual loops failing is degraded, not critical
    
    async def run(self) -> HealthCheckResult:
        cog = self.bot.get_cog("LoopCog")
        if not cog:
            return HealthCheckResult(
                self.name, HealthStatus.CRITICAL,
                "LoopCog not found. No background tasks registered."
            )
        
        # Check each loop task
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
            ("Twitch Polling", cog.pollTwitchStreams)
        ]
        
        failed_loops = []
        for name, task in loop_tasks:
            if not task.is_running():
                failed_loops.append(name)
            # Optionally check how long since last iteration
            # if task.delta and task.delta.total_seconds() > expected_interval * 3:
            #     failed_loops.append(f"{name} (stuck)")
        
        if failed_loops:
            return HealthCheckResult(
                self.name, HealthStatus.DEGRADED,
                f"Stopped loops: {', '.join(failed_loops)}",
                details={"stopped_loops": failed_loops}
            )
        
        return HealthCheckResult(
            self.name, HealthStatus.HEALTHY,
            f"All {len(loop_tasks)} background loops are running."
        )
```

## Checks

- **Critical**: No (startup check would always pass since loops start after ready)
- **Startup check**: No
- **Periodic check**: Yes (every 2 minutes - detects failures quickly)
- **Failure action**: Notify alert channel with which loop(s) stopped
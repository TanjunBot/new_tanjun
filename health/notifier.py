"""Notification helper for health check failures."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from health.checks import HealthCheckResult, HealthStatus

if TYPE_CHECKING:
    from discord.ext import commands

logger = logging.getLogger(__name__)

# Default alert channel and user ping for health check failures
# Channel: 959513664589791293 (alerts channel)
# User: 471036610561966111 (bot owner ping)
HEALTH_ALERT_CHANNEL_ID: int = 959513664589791293
HEALTH_ALERT_USER_ID: int = 471036610561966111


async def notify_health_failures(
    bot: commands.AutoShardedBot,
    failures: list[HealthCheckResult],
) -> None:
    """Send health check failure notifications to the designated Discord channel.

    Args:
        bot: The bot instance used to look up the alert channel.
        failures: List of health check results with DEGRADED or CRITICAL status.
    """
    if not failures:
        return

    import discord

    channel = bot.get_channel(HEALTH_ALERT_CHANNEL_ID)
    if not channel:
        logger.warning(
            "Health alert channel %s not found, cannot notify failures",
            HEALTH_ALERT_CHANNEL_ID,
        )
        return

    embed = discord.Embed(
        title="⚠️ Health Check Failure",
        color=0xFF0000,
        timestamp=datetime.now(),
    )

    for failure in failures:
        status_emoji = "🔴" if failure.status == HealthStatus.CRITICAL else "🟡"
        embed.add_field(
            name=f"{status_emoji} {failure.check_name}",
            value=f"**Status:** {failure.status.value}\n{failure.message}",
            inline=False,
        )

    try:
        await channel.send(
            content=f"<@{HEALTH_ALERT_USER_ID}>",
            embed=embed,
        )
        logger.info("Sent health failure notification to channel %s", HEALTH_ALERT_CHANNEL_ID)
    except Exception as exc:
        logger.error("Failed to send health failure notification: %s", exc)

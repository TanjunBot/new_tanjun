"""Notification helper for health check failures."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from health.checks import HealthCheckResult, HealthStatus

if TYPE_CHECKING:
    from discord.ext import commands

logger = logging.getLogger(__name__)

# Alert channel and user ping for health check failures, configured via env vars.
# Both must be set — no safe defaults, so misconfiguration is caught early.
_alert_channel_str = os.environ.get("HEALTH_ALERT_CHANNEL_ID")
_alert_user_str = os.environ.get("HEALTH_ALERT_USER_ID")

if _alert_channel_str is None:
    raise RuntimeError("Missing required env var: HEALTH_ALERT_CHANNEL_ID")
try:
    HEALTH_ALERT_CHANNEL_ID: int = int(_alert_channel_str)
except ValueError as exc:
    raise RuntimeError(
        f"HEALTH_ALERT_CHANNEL_ID must be an integer, got: {_alert_channel_str!r}"
    ) from exc

if _alert_user_str is None:
    raise RuntimeError("Missing required env var: HEALTH_ALERT_USER_ID")
try:
    HEALTH_ALERT_USER_ID: int = int(_alert_user_str)
except ValueError as exc:
    raise RuntimeError(
        f"HEALTH_ALERT_USER_ID must be an integer, got: {_alert_user_str!r}"
    ) from exc


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

    # Try cache first, fall back to API fetch for uncached channels
    channel = bot.get_channel(HEALTH_ALERT_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(HEALTH_ALERT_CHANNEL_ID)
        except Exception:
            channel = None

    if channel is None:
        logger.warning(
            "Health alert channel %s not found, cannot notify failures",
            HEALTH_ALERT_CHANNEL_ID,
        )
        return

    embed = discord.Embed(
        title="⚠️ Health Check Failure",
        color=0xFF0000,
        timestamp=datetime.now(timezone.utc),
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

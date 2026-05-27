"""Notification helper for health check failures."""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from health.checks import HealthCheckResult, HealthStatus

if TYPE_CHECKING:
    from discord.ext import commands

logger = logging.getLogger(__name__)


def _parse_alert_config() -> tuple[int, int]:
    """Read and validate alert config from environment variables.

    Returns:
        A tuple of (channel_id, user_id).

    Raises:
        RuntimeError: If either env var is missing or not a valid integer.
    """
    channel_str = os.environ.get("HEALTH_ALERT_CHANNEL_ID")
    user_str = os.environ.get("HEALTH_ALERT_USER_ID")

    if channel_str is None:
        raise RuntimeError("Missing required env var: HEALTH_ALERT_CHANNEL_ID")
    try:
        channel_id = int(channel_str)
    except ValueError as exc:
        raise RuntimeError(f"HEALTH_ALERT_CHANNEL_ID must be an integer, got: {channel_str!r}") from exc

    if user_str is None:
        raise RuntimeError("Missing required env var: HEALTH_ALERT_USER_ID")
    try:
        user_id = int(user_str)
    except ValueError as exc:
        raise RuntimeError(f"HEALTH_ALERT_USER_ID must be an integer, got: {user_str!r}") from exc

    return channel_id, user_id


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

    channel_id, user_id = _parse_alert_config()
    import discord

    # Try cache first, fall back to API fetch for uncached channels
    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception:
            channel = None

    if channel is None:
        logger.warning(
            "Health alert channel %s not found, cannot notify failures",
            channel_id,
        )
        return

    embed = discord.Embed(
        title="⚠️ Health Check Failure",
        color=0xFF0000,
        timestamp=datetime.now(UTC),
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
            content=f"<@{user_id}>",
            embed=embed,
        )
        logger.info("Sent health failure notification to channel %s", channel_id)
    except Exception as exc:
        logger.error("Failed to send health failure notification: %s", exc)

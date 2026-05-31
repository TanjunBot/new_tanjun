"""Notification helper for health check failures."""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from health.checks import HealthCheckResult, HealthStatus
from utility import EmbedColor

if TYPE_CHECKING:
    from discord.ext import commands

logger = logging.getLogger(__name__)


def _parse_alert_config() -> tuple[int, int] | None:
    """Read and validate alert config from environment variables.

    Returns:
        A tuple of (channel_id, user_id), or ``None`` when alerting is not configured.
    """
    channel_str = os.environ.get("HEALTH_ALERT_CHANNEL_ID")
    user_str = os.environ.get("HEALTH_ALERT_USER_ID")

    if not channel_str or not user_str:
        return None

    try:
        channel_id = int(channel_str)
    except ValueError:
        logger.warning("HEALTH_ALERT_CHANNEL_ID must be an integer, got: %r", channel_str)
        return None

    try:
        user_id = int(user_str)
    except ValueError:
        logger.warning("HEALTH_ALERT_USER_ID must be an integer, got: %r", user_str)
        return None

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

    alert_config = _parse_alert_config()
    if alert_config is None:
        logger.debug("Health alert env vars not configured; skipping failure notification")
        return

    channel_id, user_id = alert_config
    import discord

    # Try cache first, fall back to API fetch for uncached channels
    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            channel = None

    if channel is None:
        logger.warning(
            "Health alert channel %s not found, cannot notify failures",
            channel_id,
        )
        return

    # Narrow type to a channel that supports .send()
    if not hasattr(channel, "send"):
        logger.warning(
            "Channel %s does not support sending messages, cannot notify failures",
            channel_id,
        )
        return

    sendable: discord.abc.Messageable = channel  # type: ignore[assignment]

    chunks = [failures[i : i + 25] for i in range(0, len(failures), 25)]
    for idx, chunk in enumerate(chunks, start=1):
        title = f"⚠️ Health Check Failure ({idx}/{len(chunks)})" if len(chunks) > 1 else "⚠️ Health Check Failure"
        embed = discord.Embed(
            title=title,
            color=EmbedColor.ERROR.value,
            timestamp=datetime.now(UTC),
        )

        for failure in chunk:
            status_emoji = "🔴" if failure.status == HealthStatus.CRITICAL else "🟡"
            embed.add_field(
                name=f"{status_emoji} {failure.check_name}"[:256],
                value=f"**Status:** {failure.status.value}\n{failure.message}"[:1024],
                inline=False,
            )

        content = f"<@{user_id}>" if idx == 1 else None
        try:
            await sendable.send(
                content=content,
                embed=embed,
            )
        except Exception as exc:
            logger.error("Failed to send health failure notification: %s", exc)
            return
        logger.info("Sent health failure notification to channel %s", channel_id)

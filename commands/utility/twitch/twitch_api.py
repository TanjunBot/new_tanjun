"""Twitch API helpers.

Provides convenience functions for working with the TwitchService.
The service itself is in services/twitch_service.py.
"""

from __future__ import annotations

from typing import Any

import discord

from services.twitch_service import get_twitch_service


async def notify_twitch_online(client: discord.Client, uuid: str, data: dict[str, Any]) -> None:
    """Send a Twitch live notification using the TwitchService."""
    service = get_twitch_service()
    if service is None:
        return
    await service.send_live_notification(client, uuid, data)


async def get_uuid_by_twitch_name(twitch_name: str) -> str | None:
    """Look up a Twitch user UUID by their login name."""
    service = get_twitch_service()
    if service is None:
        return None
    user = await service.get_user_by_login(twitch_name)
    return user["id"] if user else None


async def subscribe_to_twitch_online_notification(twitch_uuid: str) -> None:
    """Track a new Twitch UUID in the stream status map."""
    service = get_twitch_service()
    if not twitch_uuid or service is None:
        return
    service.stream_status[twitch_uuid] = False


def parse_twitch_notification_message(message: str | None, locale: str, twitch_name: str) -> str:
    """Parse a notification message template, replacing {name} with the Twitch user's name."""
    service = get_twitch_service()
    if service is None:
        # Fallback if service not initialized
        if not message:
            from localizer import tanjunLocalizer

            return tanjunLocalizer.localize(
                locale, "commands.utility.twitch.defaultNotificationMessage"
            ).replace("{name}", twitch_name)
        return message.replace("{name}", twitch_name)
    return service._parse_notification_message(message, locale, twitch_name)

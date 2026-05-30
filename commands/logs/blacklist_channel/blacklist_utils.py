"""Shared utility functions for log blacklist management."""

from __future__ import annotations

import discord

from api import LogBlacklistType


def get_channel_blacklist_type(
    channel: discord.TextChannel | discord.VoiceChannel | discord.CategoryChannel,
) -> LogBlacklistType:
    """Determine the LogBlacklistType for a given channel based on its type."""
    if isinstance(channel, discord.CategoryChannel):
        return LogBlacklistType.CATEGORY
    if isinstance(channel, discord.VoiceChannel):
        return LogBlacklistType.VOICE_CHANNEL
    return LogBlacklistType.CHANNEL

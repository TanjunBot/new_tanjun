from __future__ import annotations

from typing import Any

import discord
from discord import app_commands


def _app_command_channel_type() -> type | None:
    cls = getattr(app_commands, 'AppCommandChannel', None)
    return cls if isinstance(cls, type) else None


def _is_partial_channel(selected: Any) -> bool:
    acc_type = _app_command_channel_type()
    if acc_type is not None and isinstance(selected, acc_type):
        return True
    return (
        hasattr(selected, 'resolve')
        and hasattr(selected, 'fetch')
        and hasattr(selected, 'guild_id')
        and not isinstance(selected, discord.abc.GuildChannel)
    )


async def resolve_guild_channel(
    guild: discord.Guild,
    selected: app_commands.AppCommandChannel | discord.abc.GuildChannel,
) -> discord.abc.GuildChannel | None:
    if isinstance(selected, discord.abc.GuildChannel):
        return selected
    if _is_partial_channel(selected):
        if selected.guild_id != guild.id:
            return None
        resolved = selected.resolve()
        if resolved is not None:
            return resolved
        try:
            return await selected.fetch()
        except (discord.NotFound, discord.Forbidden):
            return None
    return None


def resolve_guild_channel_sync(
    guild: discord.Guild,
    selected: app_commands.AppCommandChannel | discord.abc.GuildChannel,
) -> discord.abc.GuildChannel | None:
    if isinstance(selected, discord.abc.GuildChannel):
        return selected
    if _is_partial_channel(selected):
        if selected.guild_id != guild.id:
            return None
        return selected.resolve()
    return None


def channel_mention(
    selected: app_commands.AppCommandChannel | discord.abc.GuildChannel,
    resolved: discord.abc.GuildChannel | None = None,
) -> str:
    if resolved is not None:
        return resolved.mention
    acc_type = _app_command_channel_type()
    if acc_type is not None and isinstance(selected, acc_type):
        return selected.mention
    return selected.mention


def bot_can_send_messages(channel: discord.abc.GuildChannel, bot_member: discord.Member) -> bool:
    return channel.permissions_for(bot_member).send_messages

from __future__ import annotations

from typing import Any

import discord
from discord import app_commands

_SelectedChannel = (
    app_commands.AppCommandChannel
    | app_commands.AppCommandThread
    | discord.abc.GuildChannel
)
_ResolvedChannel = discord.abc.GuildChannel | discord.Thread


def _app_command_channel_type() -> type | None:
    cls = getattr(app_commands, 'AppCommandChannel', None)
    return cls if isinstance(cls, type) else None


def _app_command_thread_type() -> type | None:
    cls = getattr(app_commands, 'AppCommandThread', None)
    return cls if isinstance(cls, type) else None


def _is_partial_channel(selected: Any) -> bool:
    acc_type = _app_command_channel_type()
    if acc_type is not None and isinstance(selected, acc_type):
        return True
    thread_type = _app_command_thread_type()
    if thread_type is not None and isinstance(selected, thread_type):
        return True
    return (
        hasattr(selected, 'resolve')
        and hasattr(selected, 'fetch')
        and hasattr(selected, 'guild_id')
        and not isinstance(selected, discord.abc.GuildChannel)
    )


async def resolve_guild_channel(
    guild: discord.Guild,
    selected: _SelectedChannel,
) -> _ResolvedChannel | None:
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
    selected: _SelectedChannel,
) -> _ResolvedChannel | None:
    if isinstance(selected, discord.abc.GuildChannel):
        return selected
    if _is_partial_channel(selected):
        if selected.guild_id != guild.id:
            return None
        return selected.resolve()
    return None


def channel_mention(
    selected: _SelectedChannel,
    resolved: _ResolvedChannel | None = None,
) -> str:
    if resolved is not None:
        return resolved.mention
    acc_type = _app_command_channel_type()
    if acc_type is not None and isinstance(selected, acc_type):
        return selected.mention
    thread_type = _app_command_thread_type()
    if thread_type is not None and isinstance(selected, thread_type):
        return selected.mention
    return selected.mention


def bot_can_send_messages(channel: _ResolvedChannel, bot_member: discord.Member) -> bool:
    return channel.permissions_for(bot_member).send_messages

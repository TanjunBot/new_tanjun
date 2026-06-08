"""
``utils/checks.py`` — Centralized permission and hierarchy checks for admin commands.

Provides reusable helpers for the common authorization pattern:

1. User has the required guild/channel permission
2. Bot has the required permission
3. Executor's top role is higher than the target's
4. Bot's top role is higher than the target's

All checks return a string key (the localisation suffix) when the check
fails, or ``None`` when the check passes.
"""
from __future__ import annotations

from locale_keys import locale
from typing import Literal
import discord
from discord import app_commands
from utility import CommandInfo
from utils.discord_channels import resolve_guild_channel_sync
from utils.embeds import ErrorEmbedCategory, categorized_error_embed, categorized_warning_embed
_CheckResult = tuple[str, ErrorEmbedCategory, bool] | None

def _user_is_member_in_guild(command_info: CommandInfo) -> bool:
    """Return ``True`` if the user is a ``discord.Member`` in a guild context."""
    return isinstance(command_info.user, discord.Member) and command_info.guild is not None

def check_user_permission(command_info: CommandInfo, permission: Literal['ban_members', 'kick_members', 'moderate_members', 'manage_messages', 'manage_roles', 'manage_channels'], *, use_guild_permissions: bool=False, channel: discord.abc.GuildChannel | None=None) -> _CheckResult:
    """Verify the command executor has the required permission.

    Parameters
    ----------
    command_info
        The command context.
    permission
        The discord.Permissions attribute name to check, e.g.
        ``"ban_members"``, ``"kick_members"``.
    use_guild_permissions
        If ``True``, check ``user.guild_permissions`` instead of
        ``channel.permissions_for(user)``.  Use this when the permission
        is guild-scoped (e.g. ``kick_members``, ``ban_members``,
        ``moderate_members``, ``manage_roles``).  Keep ``False`` for
        channel-scoped permissions (e.g. ``manage_messages``).
    channel
        Optional channel to check channel-level permissions against.
        If provided, permissions are checked for this channel instead of
        the invocation channel. Only used when use_guild_permissions is False.

    Returns
    -------
    ``None`` when the check passes, otherwise a result tuple.
    """
    if not _user_is_member_in_guild(command_info):
        return ('missingPermission', ErrorEmbedCategory.PERMISSION, True)
    user = command_info.user
    assert isinstance(user, discord.Member)
    has_perm: bool
    if use_guild_permissions:
        has_perm = getattr(user.guild_permissions, permission, False)
    else:
        target_channel = channel if channel is not None else command_info.channel
        if target_channel is None or not hasattr(target_channel, 'permissions_for'):
            return ('missingPermission', ErrorEmbedCategory.PERMISSION, True)
        has_perm = getattr(target_channel.permissions_for(user), permission, False)
    if not has_perm:
        return ('missingPermission', ErrorEmbedCategory.PERMISSION, True)
    return None

def check_bot_permission(command_info: CommandInfo, permission: Literal['ban_members', 'kick_members', 'moderate_members', 'manage_messages', 'manage_roles', 'manage_channels'], *, channel: app_commands.AppCommandChannel | discord.abc.GuildChannel | None=None) -> _CheckResult:
    """Verify the bot has the required permission.

    Parameters
    ----------
    command_info
        The command context (``command_info.guild`` is expected to be set).
    permission
        The permission attribute name to check.
    channel
        Optional channel to check channel-level permissions instead of
        guild-level (e.g. for purge which needs ``manage_messages`` in
        a specific channel).

    Returns
    -------
    ``None`` on success, otherwise a result tuple.
    """
    guild = command_info.guild
    if guild is None:
        return ('missingPermissionBot', ErrorEmbedCategory.PERMISSION, True)
    if channel is not None:
        resolved = resolve_guild_channel_sync(guild, channel)
        if resolved is None or not hasattr(resolved, 'permissions_for'):
            return ('missingPermissionBot', ErrorEmbedCategory.PERMISSION, True)
        has_perm = getattr(resolved.permissions_for(guild.me), permission, False)
    else:
        has_perm = getattr(guild.me.guild_permissions, permission, False)
    if not has_perm:
        return ('missingPermissionBot', ErrorEmbedCategory.PERMISSION, True)
    return None

def check_executor_hierarchy(command_info: CommandInfo, target: discord.Member) -> _CheckResult:
    """Verify the executor's top role is higher than the target's.

    Returns ``None`` if the target is not a guild member, if the executor
    is not a guild member, or if the hierarchy is satisfied.
    """
    if not isinstance(command_info.user, discord.Member):
        return None
    if target.top_role >= command_info.user.top_role:
        return ('targetTooHigh', ErrorEmbedCategory.PERMISSION, False)
    return None

def check_bot_hierarchy(command_info: CommandInfo, target: discord.Member) -> _CheckResult:
    """Verify the bot's top role is higher than the target's."""
    guild = command_info.guild
    if guild is None:
        return ('missingPermissionBot', ErrorEmbedCategory.PERMISSION, True)
    if guild.me.top_role <= target.top_role:
        return ('targetTooHigh', ErrorEmbedCategory.PERMISSION, False)
    return None

def can_moderate(command_info: CommandInfo, target: discord.Member, user_permission: Literal['ban_members', 'kick_members', 'moderate_members'], bot_permission: Literal['ban_members', 'kick_members', 'moderate_members'], *, use_guild_permissions: bool=True) -> _CheckResult:
    """Convenience helper: run all standard admin moderation checks.

    Order: user permission → bot permission → executor hierarchy →
    bot hierarchy.  Returns the first failure (or ``None``).
    """
    result = check_user_permission(command_info, user_permission, use_guild_permissions=use_guild_permissions)
    if result is not None:
        return result
    result = check_bot_permission(command_info, bot_permission)
    if result is not None:
        return result
    result = check_executor_hierarchy(command_info, target)
    if result is not None:
        return result
    result = check_bot_hierarchy(command_info, target)
    if result is not None:
        return result
    return None

async def send_check_failure(command_info: CommandInfo, feature: str, result: _CheckResult) -> bool:
    """Send the localised failure embed for a failed check.

    Parameters
    ----------
    command_info
        The command context (used for reply and locale).
    feature
        Short feature name, e.g. ``"ban"``, ``"kick"`` — used to assemble
        the localisation key ``commands.admin.{feature}.{key}.title``.
    result
        The tuple returned by a check function.

    Returns
    -------
    ``True`` (always sent a reply).
    """
    if result is None:
        return False
    check_key, category, is_warning = result
    loc = str(command_info.locale)
    check_node = getattr(getattr(locale.commands.admin, feature), check_key)
    title = check_node.title(loc)
    description = check_node.description(loc)
    if is_warning:
        embed = categorized_warning_embed(title, description)
    else:
        embed = categorized_error_embed(category, title, description)
    reply = command_info.reply
    if reply is not None:
        await reply(embed=embed)
    return True

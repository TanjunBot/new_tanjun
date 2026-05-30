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

from typing import Literal

import discord

from utility import CommandInfo
from utils.embeds import ErrorEmbedCategory, categorized_error_embed, categorized_warning_embed

# ---------------------------------------------------------------------------
# Result type — a tuple of (embed_key_suffix, embed_category, is_warning)
# ---------------------------------------------------------------------------
# When a check fails we return enough info for the caller to build the
# appropriate embed without repeating the same boilerplate.
#
# ``check_key`` — the localisation suffix used to build the key:
#   ``commands.admin.{feature}.{check_key}.title``
#   ``commands.admin.{feature}.{check_key}.description``
#
# ``category`` — the ``ErrorEmbedCategory`` for the embed colour / icon.
#
# ``is_warning`` — ``True`` → use ``categorized_warning_embed``,
#                   ``False`` → use ``categorized_error_embed``.

_CheckResult = tuple[str, ErrorEmbedCategory, bool] | None


# ---------------------------------------------------------------------------
# Permission helpers
# ---------------------------------------------------------------------------

def _user_is_member_in_guild(
    command_info: CommandInfo,
) -> bool:
    """Return ``True`` if the user is a ``discord.Member`` in a guild channel."""
    return isinstance(command_info.user, discord.Member) and isinstance(
        command_info.channel, discord.abc.GuildChannel
    )


# ---------------------------------------------------------------------------
# User permission checks
# ---------------------------------------------------------------------------

def check_user_permission(
    command_info: CommandInfo,
    permission: Literal[
        "ban_members",
        "kick_members",
        "moderate_members",
        "manage_messages",
        "manage_roles",
        "manage_channels",
    ],
    *,
    use_guild_permissions: bool = False,
) -> _CheckResult:
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

    Returns
    -------
    ``None`` when the check passes, otherwise a result tuple.
    """
    if not _user_is_member_in_guild(command_info):
        return ("missingPermission", ErrorEmbedCategory.PERMISSION, True)

    has_perm: bool
    if use_guild_permissions:
        has_perm = getattr(command_info.user.guild_permissions, permission, False)  # type: ignore[union-attr]
    else:
        has_perm = getattr(
            command_info.channel.permissions_for(command_info.user),  # type: ignore[union-attr]
            permission,
            False,
        )

    if not has_perm:
        return ("missingPermission", ErrorEmbedCategory.PERMISSION, True)

    return None


# ---------------------------------------------------------------------------
# Bot permission checks
# ---------------------------------------------------------------------------

def check_bot_permission(
    command_info: CommandInfo,
    permission: Literal[
        "ban_members",
        "kick_members",
        "moderate_members",
        "manage_messages",
        "manage_roles",
        "manage_channels",
    ],
    *,
    channel: discord.TextChannel | None = None,
) -> _CheckResult:
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
        raise ValueError("Guild is missing in command_info")

    if channel is not None:
        has_perm = getattr(channel.permissions_for(guild.me), permission, False)
    else:
        has_perm = getattr(guild.me.guild_permissions, permission, False)

    if not has_perm:
        return ("missingPermissionBot", ErrorEmbedCategory.PERMISSION, True)

    return None


# ---------------------------------------------------------------------------
# Role-hierarchy checks
# ---------------------------------------------------------------------------

def check_executor_hierarchy(
    command_info: CommandInfo,
    target: discord.Member,
) -> _CheckResult:
    """Verify the executor's top role is higher than the target's.

    Returns ``None`` if the target is not a guild member, if the executor
    is not a guild member, or if the hierarchy is satisfied.
    """
    if not isinstance(command_info.user, discord.Member):
        return None
    if target.top_role >= command_info.user.top_role:
        return ("targetTooHigh", ErrorEmbedCategory.PERMISSION, False)
    return None


def check_bot_hierarchy(
    command_info: CommandInfo,
    target: discord.Member,
) -> _CheckResult:
    """Verify the bot's top role is higher than the target's."""
    guild = command_info.guild
    if guild is None:
        raise ValueError("Guild is missing in command_info")
    if guild.me.top_role <= target.top_role:
        return ("targetTooHighBot", ErrorEmbedCategory.PERMISSION, False)
    return None


# ---------------------------------------------------------------------------
# Compound check helpers
# ---------------------------------------------------------------------------

def can_moderate(
    command_info: CommandInfo,
    target: discord.Member,
    user_permission: Literal[
        "ban_members",
        "kick_members",
        "moderate_members",
    ],
    bot_permission: Literal[
        "ban_members",
        "kick_members",
        "moderate_members",
    ],
    *,
    use_guild_permissions: bool = True,
) -> _CheckResult:
    """Convenience helper: run all standard admin moderation checks.

    Order: user permission → bot permission → executor hierarchy →
    bot hierarchy.  Returns the first failure (or ``None``).
    """
    # 1. User permission
    result = check_user_permission(command_info, user_permission, use_guild_permissions=use_guild_permissions)
    if result is not None:
        return result

    # 2. Bot permission
    result = check_bot_permission(command_info, bot_permission)
    if result is not None:
        return result

    # 3. Executor hierarchy
    result = check_executor_hierarchy(command_info, target)
    if result is not None:
        return result

    # 4. Bot hierarchy
    result = check_bot_hierarchy(command_info, target)
    if result is not None:
        return result

    return None


# ---------------------------------------------------------------------------
# Embed builders for check failures
# ---------------------------------------------------------------------------

async def send_check_failure(
    command_info: CommandInfo,
    feature: str,
    result: _CheckResult,
) -> bool:
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

    title_key = f"commands.admin.{feature}.{check_key}.title"
    desc_key = f"commands.admin.{feature}.{check_key}.description"

    from localizer import tanjunLocalizer

    title = tanjunLocalizer.localize(str(command_info.locale), title_key)
    description = tanjunLocalizer.localize(str(command_info.locale), desc_key)

    if is_warning:
        embed = categorized_warning_embed(title, description)
    else:
        embed = categorized_error_embed(category, title, description)

    await command_info.reply(embed=embed)
    return True

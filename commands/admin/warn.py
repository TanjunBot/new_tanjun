from datetime import UTC, datetime, timedelta

import discord

import utility
from api import add_warning, get_warn_config, get_warnings
from localizer import tanjunLocalizer
from utility import CommandInfo


async def warn_user(command_info: utility.CommandInfo, member: discord.Member, reason: str | None = None) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).kick_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.missingPermission.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.missingPermission.description"),
        )
        await command_info.reply(embed=embed)
        return

    if isinstance(command_info.user, discord.Member) and member.top_role >= CommandInfo.user.top_role:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.targetTooHigh.description"),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    guild_id = CommandInfo.guild.id  # type: ignore[misc, union-attr]
    user_id = member.id

    warn_config = await get_warn_config(guild_id)

    expire_date = datetime.now(UTC) + timedelta(days=warn_config.expiration_days)

    await add_warning(guild_id, user_id, reason, expire_date, command_info.user.id)  # type: ignore[arg-type]
    warn_count = len(await get_warnings(guild_id, user_id))  # type: ignore[arg-type]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.warn.success.description",
            user=member.name,
            reason=(
                reason if reason else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.noReasonProvided")
            ),
            count=warn_count,
        ),
    )
    await command_info.reply(embed=embed)

    # Check for escalated actions based on warn count
    if warn_config:
        if warn_count >= warn_config.ban_threshold:
            # Ban the user
            await member.ban(reason=f"Reached {warn_count} warnings")
        elif warn_count >= warn_config.kick_threshold:
            # Kick the user
            await member.kick(reason=f"Reached {warn_count} warnings")
        elif warn_count >= warn_config.timeout_threshold:
            # Timeout the user
            timeout_duration = warn_config.timeout_duration
            duration = timedelta(minutes=timeout_duration)
            until = discord.utils.utcnow() + duration
            await member.timeout(until, reason=f"Reached {warn_count} warnings")

    # DM the warned user
    try:
        dm_embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.dmNotification.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.warn.dmNotification.description",
                guild=command_info.guild.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warn.noReasonProvided")
                ),
                count=warn_count,
            ),
        )
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        # If we can't DM the user, we'll just ignore it
        pass

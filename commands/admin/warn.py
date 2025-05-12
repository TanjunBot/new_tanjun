from datetime import UTC, datetime, timedelta

import discord

import utility
from api import add_warning, get_warn_config, get_warnings
from localizer import tanjunLocalizer


async def warn_user(commandInfo: utility.commandInfo, member: discord.Member, reason: str = None):
    if isinstance(commandInfo.user, discord.Member) and not commandInfo.channel.permissions_for(commandInfo.user).kick_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.missingPermission.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if member.top_role >= commandInfo.user.top_role:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.targetTooHigh.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    guild_id = commandInfo.guild.id
    user_id = member.id

    warn_config = await get_warn_config(guild_id)

    expireDate = datetime.now(UTC) + timedelta(days=warn_config["expiration_days"])

    await add_warning(guild_id, user_id, reason, expireDate, commandInfo.user.id)
    warn_count = len(await get_warnings(guild_id, user_id))

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.warn.success.description",
            user=member.name,
            reason=(
                reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.noReasonProvided")
            ),
            count=warn_count,
        ),
    )
    await commandInfo.reply(embed=embed)

    # Check for escalated actions based on warn count
    if warn_config:
        if warn_count >= warn_config["ban_threshold"]:
            # Ban the user
            await member.ban(reason=f"Reached {warn_count} warnings")
        elif warn_count >= warn_config["kick_threshold"]:
            # Kick the user
            await member.kick(reason=f"Reached {warn_count} warnings")
        elif warn_count >= warn_config["timeout_threshold"]:
            # Timeout the user
            timeout_duration = warn_config["timeout_duration"]
            duration = timedelta(minutes=timeout_duration)
            until = discord.utils.utcnow() + duration
            await member.timeout(until, reason=f"Reached {warn_count} warnings")

    # DM the warned user
    try:
        dm_embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.dmNotification.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.warn.dmNotification.description",
                guild=commandInfo.guild.name,
                reason=(
                    reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.warn.noReasonProvided")
                ),
                count=warn_count,
            ),
        )
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        # If we can't DM the user, we'll just ignore it
        pass

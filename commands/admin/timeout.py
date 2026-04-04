from datetime import timedelta

import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def timeout(
    commandInfo: utility.CommandInfo,
    member: discord.Member,
    duration: int | timedelta,
    reason: str | None = None,
) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).moderate_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.timeout.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if commandInfo.guild is None:
        raise ValueError("Guild is missing in commandInfo")

    if commandInfo.guild.me.guild_permissions.moderate_members is False:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.timeout.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if isinstance(commandInfo.user, discord.Member) and member.top_role >= CommandInfo.user.top_role:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.targetTooHigh.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        if isinstance(duration, int):
            duration = timedelta(minutes=duration)

        if member.is_timed_out() is True:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.alreadyTimedOut.title"),
                description=tanjunLocalizer.localize(
                    str(commandInfo.locale),
                    "commands.admin.timeout.alreadyTimedOut.description",
                    user=member.name,
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        until = discord.utils.utcnow() + duration
        await member.timeout(until, reason=reason)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.success.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.timeout.success.description",
                user=member.name,
                duration=str(duration),
                reason=(
                    reason
                    if reason is not None
                    else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.noReasonProvided")
                ),
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.forbidden.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.error.description"),
        )
        await commandInfo.reply(embed=embed)
    except TypeError:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.timeout.invalidDuration.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.timeout.invalidDuration.description"
            ),
        )
        await commandInfo.reply(embed=embed)

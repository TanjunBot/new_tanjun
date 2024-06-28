import discord
import utility
from localizer import tanjunLocalizer
from datetime import timedelta, datetime
from typing import Union

async def timeout(commandInfo: utility.commandInfo, member: discord.Member, duration: Union[int, timedelta], reason: str = None):
    if not commandInfo.user.guild_permissions.moderate_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.timeout.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.timeout.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.moderate_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.timeout.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.timeout.missingPermissionBot.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if member.top_role >= commandInfo.user.top_role:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.timeout.targetTooHigh.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.timeout.targetTooHigh.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        if isinstance(duration, int):
            duration = timedelta(minutes=duration)

        if member.is_timed_out():
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.admin.timeout.alreadyTimedOut.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.timeout.alreadyTimedOut.description",
                    user=member.name
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        until = discord.utils.utcnow() + duration
        await member.timeout(until, reason=reason)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.timeout.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.timeout.success.description",
                user=member.name,
                duration=str(duration),
                reason=reason if reason else tanjunLocalizer.localize(commandInfo.locale, "commands.admin.timeout.noReasonProvided")
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.timeout.forbidden.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.timeout.forbidden.description"
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.timeout.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.timeout.error.description"
            ),
        )
        await commandInfo.reply(embed=embed)
    except TypeError as e:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.timeout.invalidDuration.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.timeout.invalidDuration.description"
            ),
        )
        await commandInfo.reply(embed=embed)
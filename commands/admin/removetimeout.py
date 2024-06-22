import discord
import utility
from localizer import tanjunLocalizer
from datetime import timedelta, datetime
from typing import Union

async def remove_timeout(commandInfo: utility.commandInfo, member: discord.Member, reason: str = None):
    if not commandInfo.user.guild_permissions.moderate_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.remove_timeout.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.remove_timeout.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.moderate_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.remove_timeout.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.remove_timeout.missingPermissionBot.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if member.top_role >= commandInfo.user.top_role:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.remove_timeout.targetTooHigh.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.remove_timeout.targetTooHigh.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        if not member.is_timed_out():
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.admin.remove_timeout.notTimedOut.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.remove_timeout.notTimedOut.description",
                    user=member.name
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        await member.timeout(None, reason=reason)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.remove_timeout.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.remove_timeout.success.description",
                user=member.name,
                reason=reason if reason else tanjunLocalizer.localize(commandInfo.locale, "commands.admin.remove_timeout.noReasonProvided")
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.remove_timeout.forbidden.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.remove_timeout.forbidden.description"
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.remove_timeout.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.remove_timeout.error.description"
            ),
        )
        await commandInfo.reply(embed=embed)


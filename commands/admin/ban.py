import discord

import utility
from localizer import tanjunLocalizer


async def ban(
    commandInfo: utility.commandInfo,
    target: discord.Member,
    reason: str = None,
    delete_message_days: int = 0,
):
    if not commandInfo.user.guild_permissions.ban_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.ban_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.ban.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if target.top_role >= commandInfo.user.top_role:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.targetTooHigh.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.targetTooHigh.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        await target.ban(reason=reason, delete_message_days=delete_message_days)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.ban.success.description",
                user=target.name,
                reason=(
                    reason if reason else tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.noReasonProvided")
                ),
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.forbidden.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.error.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.ban.error.description"),
        )
        await commandInfo.reply(embed=embed)

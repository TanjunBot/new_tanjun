import discord

import utility
from localizer import tanjunLocalizer


async def change_nickname(commandInfo: utility.commandInfo, member: discord.Member, nickname: str = None):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_nicknames
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.nickname.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.manage_nicknames:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.nickname.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if member.top_role >= commandInfo.user.top_role and commandInfo.user != commandInfo.guild.owner:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.targetTooHigh.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        old_nick = member.nick or member.name
        await member.edit(nick=nickname)
        if nickname:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.changed.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.nickname.changed.description",
                    user=member.mention,
                    old_nick=old_nick,
                    new_nick=nickname,
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.removed.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.nickname.removed.description",
                    user=member.name,
                    old_nick=old_nick,
                ),
            )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.forbidden.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nickname.error.description"),
        )
        await commandInfo.reply(embed=embed)

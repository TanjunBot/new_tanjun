import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def change_nickname(command_info: utility.CommandInfo, member: discord.Member, nickname: str | None = None) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_nicknames
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.nickname.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.manage_nicknames:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.nickname.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if (
        isinstance(command_info.user, discord.Member)
        and member.top_role >= CommandInfo.user.top_role  # type: ignore[misc, union-attr]
        and command_info.user != CommandInfo.guild.owner  # type: ignore[misc, union-attr]
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.targetTooHigh.description"),
        )
        await command_info.reply(embed=embed)
        return

    try:
        old_nick = member.nick or member.name
        await member.edit(nick=nickname)
        if nickname:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.changed.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.nickname.changed.description",
                    user=member.mention,
                    old_nick=old_nick,
                    new_nick=nickname,
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.removed.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.nickname.removed.description",
                    user=member.name,
                    old_nick=old_nick,
                ),
            )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nickname.error.description"),
        )
        await command_info.reply(embed=embed)

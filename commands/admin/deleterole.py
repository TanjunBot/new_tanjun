import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def deleterole(command_info: utility.CommandInfo, role: discord.Role, reason: str | None = None) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.deleterole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.deleterole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    assert command_info.client.user is not None
    bot_member = CommandInfo.guild.get_member(command_info.client.user.id)  # type: ignore[misc, union-attr]
    if not bot_member or not bot_member.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.deleterole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.deleterole.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if isinstance(command_info.user, discord.Member) and command_info.user.top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.deleterole.roleTooHigh.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.deleterole.roleTooHigh.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if bot_member and bot_member.top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.deleterole.roleTooHighBot.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.deleterole.roleTooHighBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    role_name: str = str(role.name)
    await role.delete(reason=reason)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.deleterole.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.admin.deleterole.success.description",
            role=role_name,
            reason=reason if reason else "None",
        ),
    )
    await command_info.reply(embed=embed)
    return

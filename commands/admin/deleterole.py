import discord

import utility
from localizer import tanjunLocalizer


async def deleterole(commandInfo: utility.CommandInfo, role: discord.Role, reason: str | None = None) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.deleterole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.deleterole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    assert commandInfo.client.user is not None
    bot_member = CommandInfo.guild.get_member(commandInfo.client.user.id)
    if not bot_member or not bot_member.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.deleterole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.deleterole.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if isinstance(commandInfo.user, discord.Member) and commandInfo.user.top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.deleterole.roleTooHigh.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.deleterole.roleTooHigh.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if bot_member and bot_member.top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.deleterole.roleTooHighBot.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.deleterole.roleTooHighBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    role_name: str = str(role.name)
    await role.delete(reason=reason)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.deleterole.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.admin.deleterole.success.description",
            role=role_name,
            reason=reason if reason else "None",
        ),
    )
    await commandInfo.reply(embed=embed)
    return

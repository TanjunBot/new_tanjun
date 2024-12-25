import discord
import utility
from localizer import tanjunLocalizer


async def deleterole(
    commandInfo: utility.commandInfo, role: discord.Role, reason: str = None
):
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.deleterole.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.deleterole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.get_member(
        commandInfo.client.user.id
    ).guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.deleterole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.deleterole.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if commandInfo.user.top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.deleterole.roleTooHigh.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.deleterole.roleTooHigh.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if (
        commandInfo.guild.get_member(commandInfo.client.user.id).top_role.position
        <= role.position
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.deleterole.roleTooHighBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.deleterole.roleTooHighBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    role_name = role.name
    await role.delete(reason=reason)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.deleterole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.deleterole.success.description",
            role=role_name,
            reason=reason,
        ),
    )
    await commandInfo.reply(embed=embed)
    return

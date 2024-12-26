import discord
import utility
from localizer import tanjunLocalizer


async def copyrole(
    commandInfo: utility.commandInfo, role: discord.Role, copy_members: bool = False
):

    if not commandInfo.user.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.copyrole.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.copyrole.missingPermission.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.get_member(
        commandInfo.client.user.id
    ).guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.copyrole.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.copyrole.missingPermissionBot.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    reasonLocale = tanjunLocalizer.localize(
        commandInfo.locale, "commands.admin.copyrole.reason", name=role.name
    )

    newRole = await commandInfo.guild.create_role(
        name=role.name,
        color=role.color,
        hoist=role.hoist,
        mentionable=role.mentionable,
        permissions=role.permissions,
        display_icon=role.icon if role.icon else role.unicode_emoji,
        reason=reasonLocale,
    )

    if copy_members:
        for member in role.members:
            await member.add_roles(newRole)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.copyrole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.copyrole.success.description",
        ),
    )

    await commandInfo.reply(embed=embed)
    await newRole.edit(reason=reasonLocale, position=role.position)
    return

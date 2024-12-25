from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import remove_level_role, get_level_roles
import discord


async def remove_level_role_command(
    commandInfo: commandInfo, role: discord.Role, level: int
):
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.removelevelrole.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.removelevelrole.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    existing_roles = await get_level_roles(str(commandInfo.guild.id), level)
    if str(role.id) not in existing_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.removelevelrole.error.role_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.removelevelrole.error.role_not_found.description",
                level=level,
                role=role.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_level_role(str(commandInfo.guild.id), str(role.id), level)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.removelevelrole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.removelevelrole.success.description",
            role=role.mention,
            level=level,
        ),
    )
    await commandInfo.reply(embed=embed)

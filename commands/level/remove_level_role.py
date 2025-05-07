import discord

from api import get_level_role, remove_level_role
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def remove_level_role_command(commandInfo: commandInfo, role: discord.Role):
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

    existing_role = await get_level_role(str(commandInfo.guild.id), str(role.id))
    if not existing_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.removelevelrole.error.role_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.removelevelrole.error.role_not_found.description",
                role=role.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_level_role(str(commandInfo.guild.id), str(role.id))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.level.removelevelrole.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.removelevelrole.success.description",
            role=role.mention,
        ),
    )
    await commandInfo.reply(embed=embed)

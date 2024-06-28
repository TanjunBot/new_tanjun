from utility import commandInfo, tanjunEmbed, checkIfHasPro
from localizer import tanjunLocalizer
from api import add_level_role, get_level_roles
import discord

async def add_level_role_command(commandInfo: commandInfo, role: discord.Role, level: int):
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.addlevelrole.error.no_permission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.addlevelrole.error.no_permission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if level < 1:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.addlevelrole.error.invalid_level.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.addlevelrole.error.invalid_level.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    existing_roles = [role[1] for role in await get_level_roles(str(commandInfo.guild.id))]
    if str(role.id) in existing_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.addlevelrole.error.role_exists.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.addlevelrole.error.role_exists.description",
                level=level,
                role=role.mention
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_level_role(str(commandInfo.guild.id), str(role.id), level)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.addlevelrole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.addlevelrole.success.description",
            role=role.mention,
            level=level
        ),
    )
    await commandInfo.reply(embed=embed)
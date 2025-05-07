import discord

import utility
from api import add_booster_role, get_booster_role
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def setupBoosterRole(commandInfo: commandInfo, role: discord.Role):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterrole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterrole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    booster_role = await get_booster_role(commandInfo.guild.id)
    if booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterrole.already_set.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterrole.already_set.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_booster_role(commandInfo.guild.id, role.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.setupboosterrole.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.setupboosterrole.success.description"),
    )
    await commandInfo.reply(embed=embed)

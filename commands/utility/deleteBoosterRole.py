from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import get_booster_role, delete_booster_role
import utility
import discord

async def deleteBoosterRole(commandInfo: commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.utility.deleteboosterrole.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.utility.deleteboosterrole.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 

    booster_role = await get_booster_role(commandInfo.guild.id)
    if not booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterrole.no_booster_role.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterrole.no_booster_role.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await delete_booster_role(commandInfo.guild.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.deleteboosterrole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.deleteboosterrole.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)

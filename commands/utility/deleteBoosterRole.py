import discord

import utility
from api import delete_booster_role, get_booster_role
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def deleteBoosterRole(commandInfo: commandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterrole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterrole.missingPermission.description",
            ),
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
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.deleteboosterrole.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale), "commands.utility.deleteboosterrole.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)

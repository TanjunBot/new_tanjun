from api import add_blacklist_role as add_blacklist_role_api
import discord
import utility
from localizer import tanjunLocalizer


async def add_blacklist_role(
    commandInfo: utility.commandInfo,
    role: discord.Role,
):
    if not commandInfo.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_role.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_role.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if role in commandInfo.guild.blacklist_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_role.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_role.alreadyBlacklisted.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_blacklist_role_api(commandInfo.guild.id, role.id)
    await commandInfo.guild.save()
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.giveaway.add_blacklist_role.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.add_blacklist_role.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
    return

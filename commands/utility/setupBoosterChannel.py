import discord

import utility
from api import add_booster_channel, get_booster_channel
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def setupBoosterChannel(commandInfo: commandInfo, category: discord.CategoryChannel) -> None:
    if isinstance(commandInfo.user, discord.User) or commandInfo.guild is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "errors.guildonly.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "errors.guildonly.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if isinstance(commandInfo.user, discord.Member) and not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterchannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterchannel.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    booster_channel = await get_booster_channel(commandInfo.guild.id)
    if booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterchannel.already_set.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterchannel.already_set.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_booster_channel(commandInfo.guild.id, category.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.setupboosterchannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.setupboosterchannel.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)

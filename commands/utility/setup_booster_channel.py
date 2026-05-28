import discord

import utility
from api import add_booster_channel, get_booster_channel
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def setupBoosterChannel(command_info: CommandInfo, category: discord.CategoryChannel) -> None:
    if isinstance(command_info.user, discord.User) or command_info.guild is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildonly.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildonly.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not getattr(command_info.user, "guild_permissions", None) or not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterchannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterchannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    booster_channel = await get_booster_channel(command_info.guild.id)
    if booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterchannel.already_set.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterchannel.already_set.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await add_booster_channel(command_info.guild.id, category.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.setupboosterchannel.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.setupboosterchannel.success.description",
        ),
    )
    await command_info.reply(embed=embed)

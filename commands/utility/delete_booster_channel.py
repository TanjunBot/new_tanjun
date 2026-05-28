import discord

import utility
from api import delete_booster_channel, get_booster_channel
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def deleteBoosterChannel(command_info: CommandInfo) -> None:
    if command_info.guild is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.channel is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if (
        isinstance(command_info.user, discord.Member)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterchannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterchannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    booster_channel = await get_booster_channel(command_info.guild.id)
    if not booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterchannel.no_booster_channel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterchannel.no_booster_channel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await delete_booster_channel(command_info.guild.id, booster_channel)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.deleteboosterchannel.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.deleteboosterchannel.success.description",
        ),
    )
    await command_info.reply(embed=embed)

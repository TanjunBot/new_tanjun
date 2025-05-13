import discord

import utility
from api import get_join_to_create_channel, set_join_to_create_channel
from localizer import tanjunLocalizer


async def jointocreatechannel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.jointocreatechannel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.jointocreatechannel.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await get_join_to_create_channel(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.jointocreatechannel.alreadySet.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.jointocreatechannel.alreadySet.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_join_to_create_channel(commandInfo.guild.id, channel.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.jointocreatechannel.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale), "commands.admin.jointocreatechannel.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)

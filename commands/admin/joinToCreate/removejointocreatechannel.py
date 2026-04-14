import discord

import utility
from api import get_join_to_create_channel, remove_join_to_create_channel
from localizer import tanjunLocalizer


async def removejointocreatechannel(commandInfo: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removejointocreatechannel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removejointocreatechannel.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not await get_join_to_create_channel(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.removejointocreatechannel.alreadySet.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removejointocreatechannel.alreadySet.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_join_to_create_channel(commandInfo.guild.id, channel.id)  # type: ignore[call-arg, union-attr]
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.removejointocreatechannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.removejointocreatechannel.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)

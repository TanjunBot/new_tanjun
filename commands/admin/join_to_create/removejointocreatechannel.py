import discord

import utility
from api import get_join_to_create_channel, remove_join_to_create_channel
from localizer import tanjunLocalizer


async def removejointocreatechannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.removejointocreatechannel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.removejointocreatechannel.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not await get_join_to_create_channel(str(channel.id)):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.removejointocreatechannel.alreadySet.title"
            ),
            description=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.removejointocreatechannel.alreadySet.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_join_to_create_channel(command_info.guild.id, channel.id)  # type: ignore[call-arg, union-attr]
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removejointocreatechannel.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale, "commands.admin.removejointocreatechannel.success.description"
        ),
    )
    await command_info.reply(embed=embed)

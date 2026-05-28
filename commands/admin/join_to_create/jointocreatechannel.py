import discord

import utility
from api import get_join_to_create_channel, set_join_to_create_channel
from localizer import tanjunLocalizer


async def jointocreatechannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.jointocreatechannel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.jointocreatechannel.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await get_join_to_create_channel(str(channel.id)):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.jointocreatechannel.alreadySet.title"),
            description=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.jointocreatechannel.alreadySet.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_join_to_create_channel(command_info.guild.id, channel.id)  # type: ignore[union-attr]
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.jointocreatechannel.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale), "commands.admin.jointocreatechannel.success.description"
        ),
    )
    await command_info.reply(embed=embed)

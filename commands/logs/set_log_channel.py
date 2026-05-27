import discord

import utility
from api import (
    get_log_channel as get_log_channel_api,
)
from api import (
    set_log_channel as set_log_channel_api,
)
from localizer import tanjunLocalizer
from utility import CommandInfo


async def set_log_channel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.setLogChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.setLogChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    assert command_info.client.user is not None
    self_member = CommandInfo.guild.get_member(command_info.client.user.id)  # type: ignore[misc, union-attr]
    permissions = channel.permissions_for(self_member)  # type: ignore[arg-type]

    if not permissions.send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.setLogChannel.botMissingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.setLogChannel.botMissingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    log_channel = await get_log_channel_api(command_info.guild.id)

    if log_channel:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.setLogChannel.alreadySet.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.logs.setLogChannel.alreadySet.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_log_channel_api(command_info.guild.id, channel.id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.setLogChannel.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.logs.setLogChannel.success.description",
            channel=channel.mention,
        ),
    )
    await command_info.reply(embed=embed)

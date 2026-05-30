import discord

import utility
from api import LogBlacklistType, is_log_entity_blacklisted, remove_log_blacklist
from commands.logs.blacklist_channel.blacklist_utils import get_channel_blacklist_type
from localizer import tanjunLocalizer


async def blacklist_remove_channel(command_info: utility.CommandInfo, channel: discord.TextChannel | discord.VoiceChannel | discord.CategoryChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    blacklist_type = get_channel_blacklist_type(channel)
    is_blacklisted = await is_log_entity_blacklisted(
        command_info.guild.id, str(channel.id), blacklist_type,
    )

    if not is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.notBlacklisted.description",
            ),
        )
    else:
        await remove_log_blacklist(command_info.guild.id, str(channel.id), blacklist_type)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistRemoveChannel.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.success.description",
            ),
        )

    await command_info.reply(embed=embed)

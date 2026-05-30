import discord

import utility
from api import LogBlacklistType, add_log_blacklist, is_log_entity_blacklisted
from localizer import tanjunLocalizer


async def blacklist_voice(command_info: utility.CommandInfo, channel: discord.VoiceChannel) -> None:
    if isinstance(command_info.user, discord.Member) and not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistVoiceChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistVoiceChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(channel.id), LogBlacklistType.VOICE_CHANNEL)

    if is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistVoiceChannel.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistVoiceChannel.alreadyBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist(command_info.guild.id, str(channel.id), LogBlacklistType.VOICE_CHANNEL)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistVoiceChannel.blacklisted.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistVoiceChannel.blacklisted.description",
            ),
        )

    await command_info.reply(embed=embed)

import discord

import utility
from api import LogBlacklistType, is_log_entity_blacklisted, remove_log_blacklist
from localizer import tanjunLocalizer


async def blacklist_remove_category(command_info: utility.CommandInfo, channel: discord.CategoryChannel) -> None:
    if not (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveCategory.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveCategory.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(channel.id), LogBlacklistType.CATEGORY)

    if not is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveCategory.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveCategory.notBlacklisted.description",
            ),
        )
    else:
        await remove_log_blacklist(command_info.guild.id, str(channel.id), LogBlacklistType.CATEGORY)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistRemoveCategory.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveCategory.success.description",
            ),
        )

    await command_info.reply(embed=embed)

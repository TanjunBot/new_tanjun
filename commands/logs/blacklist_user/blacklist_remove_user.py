import discord

import utility
from api import LogBlacklistType
from localizer import tanjunLocalizer


async def blacklist_remove_user(command_info: utility.CommandInfo, user: discord.Member) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveUser.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveUser.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted_api(command_info.guild.id, user.id, LogBlacklistType.USER)

    if not is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveUser.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveUser.notBlacklisted.description",
            ),
        )
    else:
        await remove_log_blacklist_api(command_info.guild.id, user.id, LogBlacklistType.USER)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistRemoveUser.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveUser.success.description",
            ),
        )

    await command_info.reply(embed=embed)

import discord

import utility
from api import LogBlacklistType
from localizer import tanjunLocalizer


async def blacklist_user(command_info: utility.CommandInfo, user: discord.Member) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistUser.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistUser.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted_api(command_info.guild.id, user.id, LogBlacklistType.USER)

    if is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistUser.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistUser.alreadyBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist_api(command_info.guild.id, user.id, LogBlacklistType.USER)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistUser.blacklisted.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistUser.blacklisted.description",
            ),
        )

    await command_info.reply(embed=embed)

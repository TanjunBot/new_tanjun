import discord

import utility
from api import LogBlacklistType, add_log_blacklist, is_log_entity_blacklisted
from localizer import tanjunLocalizer


async def blacklist_role(command_info: utility.CommandInfo, role: discord.Role) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(role.id), LogBlacklistType.ROLE)

    if is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRole.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRole.alreadyBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist(command_info.guild.id, str(role.id), LogBlacklistType.ROLE)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistRole.blacklisted.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRole.blacklisted.description",
            ),
        )

    await command_info.reply(embed=embed)

import discord

import utility
from api import (
    add_log_role_blacklist as add_log_blacklist_role_api,
)
from api import (
    is_log_role_blacklisted as is_log_role_blacklisted_api,
)
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
    is_blacklisted = await is_log_role_blacklisted_api(command_info.guild.id, role.id)

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
        await add_log_blacklist_role_api(command_info.guild.id, role.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistRole.blacklisted.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRole.blacklisted.description",
            ),
        )

    await command_info.reply(embed=embed)

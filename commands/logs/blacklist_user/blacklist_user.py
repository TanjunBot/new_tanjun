import discord

import utility
from api import (
    get_log_user_blacklist as add_log_blacklist_user_api,
)
from api import (
    is_log_user_blacklisted as is_log_user_blacklisted_api,
)
from localizer import tanjunLocalizer


async def blacklist_user(commandInfo: utility.CommandInfo, user: discord.Member) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    isBlacklisted = await is_log_user_blacklisted_api(commandInfo.guild.id, user.id)

    if isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.alreadyBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist_user_api(commandInfo.guild.id, user.id)  # type: ignore[call-arg]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.blacklistUser.blacklisted.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.blacklisted.description",
            ),
        )

    await commandInfo.reply(embed=embed)

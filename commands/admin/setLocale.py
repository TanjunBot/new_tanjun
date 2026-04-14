import discord

import utility
from localizer import tanjunLocalizer


async def set_locale(commandInfo: utility.CommandInfo, locale: str) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_guild
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.setLocale.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if commandInfo.guild is None:
        raise ValueError("Guild is missing in commandInfo")

    await commandInfo.guild.edit(
        preferred_locale=locale,  # type: ignore[arg-type]
        reason=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.setLocaleReason"),
    )
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.success.description"),
    )
    await commandInfo.reply(embed=embed)
    return None

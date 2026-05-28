import discord

import utility
from localizer import tanjunLocalizer


async def set_locale(command_info: utility.CommandInfo, locale: str) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_guild
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.setLocale.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.setLocale.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.guild is None:
        raise ValueError("Guild is missing in command_info")

    await command_info.guild.edit(
        preferred_locale=locale,  # type: ignore[arg-type]
        reason=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.setLocale.setLocaleReason"),
    )
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.setLocale.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.setLocale.success.description"),
    )
    await command_info.reply(embed=embed)
    return None

import discord

from api import get_level_system_status, set_level_system_status
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def enable_level_system(commandInfo: CommandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.enablelevelsystem.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.enablelevelsystem.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    current_status = bool(await get_level_system_status(str(commandInfo.guild.id)))

    if current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.enablelevelsystem.error.already_enabled.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.enablelevelsystem.error.already_enabled.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_level_system_status(str(commandInfo.guild.id), True)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.enablelevelsystem.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.enablelevelsystem.success.description"),
    )
    await commandInfo.reply(embed=embed)

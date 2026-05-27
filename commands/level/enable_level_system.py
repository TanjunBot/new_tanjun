import discord

from api import get_level_system_status, set_level_system_status
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def enable_level_system(command_info: CommandInfo) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.enablelevelsystem.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.enablelevelsystem.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    current_status = bool(await get_level_system_status(str(command_info.guild.id)))

    if current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.enablelevelsystem.error.already_enabled.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.enablelevelsystem.error.already_enabled.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_level_system_status(str(command_info.guild.id), True)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.enablelevelsystem.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.level.enablelevelsystem.success.description"),
    )
    await command_info.reply(embed=embed)

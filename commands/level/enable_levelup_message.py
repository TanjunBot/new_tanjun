import discord

from api import get_levelup_message_status, set_levelup_message_status
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def enable_levelup_message(command_info: CommandInfo) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.enablelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.enablelevelupmessage.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.guild is None:
        raise ValueError("Guild is missing in command_info")

    current_status: bool = bool(await get_levelup_message_status(str(command_info.guild.id)))
    if current_status is True:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.enablelevelupmessage.error.already_enabled.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_levelup_message_status(str(command_info.guild.id), True)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.enablelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.level.enablelevelupmessage.success.description",
        ),
    )
    await command_info.reply(embed=embed)

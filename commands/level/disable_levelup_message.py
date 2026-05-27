import discord

from api import get_levelup_message_status, set_levelup_message_status
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def disable_levelup_message(command_info: CommandInfo) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.disablelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.disablelevelupmessage.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    current_status = bool(await get_levelup_message_status(str(command_info.guild.id)))
    if not current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.disablelevelupmessage.error.already_disabled.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.disablelevelupmessage.error.already_disabled.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_levelup_message_status(str(command_info.guild.id), False)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.disablelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.level.disablelevelupmessage.success.description",
        ),
    )
    await command_info.reply(embed=embed)

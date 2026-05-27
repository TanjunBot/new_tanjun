import discord

from api import set_levelup_message
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def change_levelup_message(command_info: CommandInfo, new_message: str) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.changelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.changelevelupmessage.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if len(new_message) > 255:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.changelevelupmessage.error.message_too_long.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.changelevelupmessage.error.message_too_long.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_levelup_message(str(command_info.guild.id), new_message)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.changelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.level.changelevelupmessage.success.description",
            new_message=new_message,
        ),
    )
    await command_info.reply(embed=embed)

import discord

from api import set_levelup_message
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def change_levelup_message(commandInfo: CommandInfo, new_message: str) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.changelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.changelevelupmessage.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if len(new_message) > 255:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.changelevelupmessage.error.message_too_long.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.changelevelupmessage.error.message_too_long.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_levelup_message(str(commandInfo.guild.id), new_message)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.changelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.level.changelevelupmessage.success.description",
            new_message=new_message,
        ),
    )
    await commandInfo.reply(embed=embed)

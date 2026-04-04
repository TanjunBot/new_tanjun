import discord  # type: ignore[import-not-found]

from api import get_levelup_message_status, set_levelup_message_status
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def enable_levelup_message(commandInfo: CommandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.enablelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.enablelevelupmessage.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if commandInfo.guild is None:
        raise ValueError("Guild is missing in commandInfo")

    current_status: bool = bool(await get_levelup_message_status(str(commandInfo.guild.id)))
    if current_status is True:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.enablelevelupmessage.error.already_enabled.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_levelup_message_status(str(commandInfo.guild.id), True)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.enablelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.level.enablelevelupmessage.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)

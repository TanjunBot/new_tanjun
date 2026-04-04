import discord  # type: ignore[import-not-found]

from api import set_levelup_channel
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def set_levelup_channel_command(commandInfo: CommandInfo, channel: discord.TextChannel | None = None) -> None:  # type: ignore[no-any-unimported]
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.setlevelupchannel.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.setlevelupchannel.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    if channel:
        await set_levelup_channel(str(commandInfo.guild.id), str(channel.id))
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.setlevelupchannel.success.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.setlevelupchannel.success.description",
                channel=channel.mention,
            ),
        )
    else:
        await set_levelup_channel(str(commandInfo.guild.id), None)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.setlevelupchannel.reset.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.level.setlevelupchannel.reset.description"
            ),
        )

    await commandInfo.reply(embed=embed)

import discord

from api import set_levelup_channel
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def set_levelup_channel_command(command_info: CommandInfo, channel: discord.TextChannel | None = None) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.setlevelupchannel.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.setlevelupchannel.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if channel:
        await set_levelup_channel(str(command_info.guild.id), str(channel.id))
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.setlevelupchannel.success.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.setlevelupchannel.success.description",
                channel=channel.mention,
            ),
        )
    else:
        await set_levelup_channel(str(command_info.guild.id), None)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.setlevelupchannel.reset.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.level.setlevelupchannel.reset.description"
            ),
        )

    await command_info.reply(embed=embed)

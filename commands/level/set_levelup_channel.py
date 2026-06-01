from locale_keys import locale
import discord
from api import set_levelup_channel
from utility import CommandInfo, tanjunEmbed

async def set_levelup_channel_command(command_info: CommandInfo, channel: discord.TextChannel | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.setlevelupchannel.error.no_permission.title(str(command_info.locale)), description=locale.commands.level.setlevelupchannel.error.no_permission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if channel:
        await set_levelup_channel(str(command_info.guild.id), str(channel.id))
        embed = tanjunEmbed(title=locale.commands.level.setlevelupchannel.success.title(str(command_info.locale)), description=locale.commands.level.setlevelupchannel.success.description(str(command_info.locale), channel=channel.mention))
    else:
        await set_levelup_channel(str(command_info.guild.id), None)
        embed = tanjunEmbed(title=locale.commands.level.setlevelupchannel.reset.title(str(command_info.locale)), description=locale.commands.level.setlevelupchannel.reset.description(str(command_info.locale)))
    await command_info.reply(embed=embed)
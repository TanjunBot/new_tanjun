from locale_keys import locale
import discord
import utility
from utility import EmbedColor

async def say(command_info: utility.CommandInfo, channel: discord.TextChannel, *, message: str) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_messages):
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.say.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.say.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).send_messages:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.say.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.say.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    try:
        await channel.send(message)
        embed = utility.tanjunEmbed(colour=EmbedColor.SUCCESS, title=locale.commands.admin.say.success.title(str(command_info.locale)), description=locale.commands.admin.say.success.description(command_info.locale, channel=channel.mention))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.say.error.title(str(command_info.locale)), description=locale.commands.admin.say.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
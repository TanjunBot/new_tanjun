from locale_keys import locale
from typing import cast
import discord
import utility

async def set_slowmode(command_info: utility.CommandInfo, seconds: int, channel: discord.TextChannel | None=None) -> None:
    if channel is None:
        assert command_info.channel is not None
        channel = cast(discord.TextChannel, command_info.channel)
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.admin.slowmode.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.slowmode.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).manage_channels:
        embed = utility.tanjunEmbed(title=locale.commands.admin.slowmode.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.slowmode.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if seconds < 0 or seconds > 21600:
        embed = utility.tanjunEmbed(title=locale.commands.admin.slowmode.invalidDuration.title(str(command_info.locale)), description=locale.commands.admin.slowmode.invalidDuration.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    try:
        await channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            embed = utility.tanjunEmbed(title=locale.commands.admin.slowmode.disabled.title(str(command_info.locale)), description=locale.commands.admin.slowmode.disabled.description(command_info.locale, channel=channel.mention))
        else:
            embed = utility.tanjunEmbed(title=locale.commands.admin.slowmode.enabled.title(str(command_info.locale)), description=locale.commands.admin.slowmode.enabled.description(command_info.locale, channel=channel.mention, seconds=seconds))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.slowmode.forbidden.title(str(command_info.locale)), description=locale.commands.admin.slowmode.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.slowmode.error.title(str(command_info.locale)), description=locale.commands.admin.slowmode.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
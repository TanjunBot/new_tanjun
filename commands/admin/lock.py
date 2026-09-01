from locale_keys import locale
from typing import cast
import discord
import utility
from api import clear_channel_overwrites, save_channel_overwrites
from utils.checks import check_bot_permission, check_user_permission, send_check_failure

async def lock_channel(command_info: utility.CommandInfo, channel: discord.TextChannel | None=None) -> None:
    if channel is None:
        if command_info.channel is None:
            raise ValueError('Channel is missing in command_info')
        channel = cast(discord.TextChannel, command_info.channel)
    result = check_user_permission(command_info, 'manage_channels', use_guild_permissions=False, channel=channel)
    if await send_check_failure(command_info, 'lock', result):
        return
    result = check_bot_permission(command_info, 'manage_channels', channel=channel)
    if await send_check_failure(command_info, 'lock', result):
        return
    try:
        await clear_channel_overwrites(channel.id)
        for target, overwrites in channel.overwrites.items():
            if isinstance(target, discord.Role):
                raw_values = cast(dict[str, bool | None], getattr(overwrites, '_values', {}))
                overwrite_dict: dict[str, bool] = {k: v for k, v in raw_values.items() if v is not None}
                await save_channel_overwrites(channel.id, target.id, overwrite_dict)
                overwrites.send_messages = False
                await channel.set_permissions(target, overwrite=overwrites)
        default_permissions = channel.overwrites_for(channel.guild.default_role)
        default_permissions.send_messages = False
        await channel.set_permissions(channel.guild.default_role, overwrite=default_permissions)
        embed = utility.tanjunEmbed(title=locale.commands.admin.lock.success.title(str(command_info.locale)), description=locale.commands.admin.lock.success.description(str(command_info.locale), channel=channel.mention))
        await command_info.reply(embed=embed)
        locked_message = locale.commands.admin.lock.channelLockedMessage(str(command_info.locale), channel=channel.mention)
        await channel.send(locked_message)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.lock.forbidden.title(str(command_info.locale)), description=locale.commands.admin.lock.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.lock.error.title(str(command_info.locale)), description=locale.commands.admin.lock.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
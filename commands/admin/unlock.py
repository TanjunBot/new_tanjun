from locale_keys import locale
import json
from typing import cast
import discord
import utility
from api import clear_channel_overwrites, get_channel_overwrites
from utils.checks import check_bot_permission, check_user_permission, send_check_failure

async def unlock_channel(command_info: utility.CommandInfo, channel: discord.TextChannel | None=None) -> None:
    if channel is None:
        if command_info.channel is None:
            raise ValueError('Channel is missing in command_info')
        channel = cast(discord.TextChannel, command_info.channel)
    result = check_user_permission(command_info, 'manage_channels', use_guild_permissions=False, channel=channel)
    if await send_check_failure(command_info, 'unlock', result):
        return
    result = check_bot_permission(command_info, 'manage_channels', channel=channel)
    if await send_check_failure(command_info, 'unlock', result):
        return
    try:
        saved_overwrites_found = False
        async for overwrite_record in get_channel_overwrites(channel.id):
            saved_overwrites_found = True
            role = channel.guild.get_role(int(overwrite_record.role_id))
            if role is not None:
                overwrite_dict = json.loads(overwrite_record.overwrites) if isinstance(overwrite_record.overwrites, str) else overwrite_record.overwrites
                overwrite = discord.PermissionOverwrite(**overwrite_dict)
                await channel.set_permissions(role, overwrite=overwrite)
        if saved_overwrites_found:
            await clear_channel_overwrites(channel.id)
        else:
            default_permissions = channel.overwrites_for(channel.guild.default_role)
            default_permissions.send_messages = None
            await channel.set_permissions(channel.guild.default_role, overwrite=default_permissions)
        embed = utility.tanjunEmbed(title=locale.commands.admin.unlock.success.title(str(command_info.locale)), description=locale.commands.admin.unlock.success.description(command_info.locale, channel=channel.mention))
        await command_info.reply(embed=embed)
        unlocked_message = locale.commands.admin.unlock.channelUnlockedMessage(str(command_info.locale), channel=channel.mention)
        await channel.send(unlocked_message)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.unlock.forbidden.title(str(command_info.locale)), description=locale.commands.admin.unlock.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.unlock.error.title(str(command_info.locale)), description=locale.commands.admin.unlock.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
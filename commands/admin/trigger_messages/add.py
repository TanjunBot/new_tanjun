from locale_keys import locale
import discord
import utility
from services.trigger_message_service import trigger_message_service

async def add_trigger_message(command_info: utility.CommandInfo, trigger: str, response: str, case_sensitive: bool=False) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.admin.trigger_messages.add.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.trigger_messages.add.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    await trigger_message_service.create(command_info.guild.id, trigger, response, case_sensitive)
    embed = utility.tanjunEmbed(title=locale.commands.admin.trigger_messages.add.success.title(str(command_info.locale)), description=locale.commands.admin.trigger_messages.add.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)
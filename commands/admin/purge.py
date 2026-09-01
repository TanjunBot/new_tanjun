from locale_keys import locale
from typing import cast
import discord
import utility
from utils.checks import check_bot_permission, check_user_permission, send_check_failure

async def purge(command_info: utility.CommandInfo, amount: int, channel: discord.TextChannel | None=None, setting: str='all') -> None:
    if command_info.guild is None:
        embed = utility.tanjunEmbed(title=locale.errors.guildOnly.title(str(command_info.locale)), description=locale.errors.guildOnly.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if channel is None:
        assert command_info.channel is not None
        channel = cast(discord.TextChannel, command_info.channel)
    result = check_user_permission(command_info, 'manage_messages', use_guild_permissions=False, channel=channel)
    if await send_check_failure(command_info, 'purge', result):
        return
    result = check_bot_permission(command_info, 'manage_messages', channel=channel)
    if await send_check_failure(command_info, 'purge', result):
        return
    if amount <= 0:
        embed = utility.tanjunEmbed(title=locale.commands.admin.purge.invalidAmount.title(str(command_info.locale)), description=locale.commands.admin.purge.invalidAmount.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    try:

        def check(m: discord.Message) -> bool:
            if setting == 'all':
                return True
            elif setting == 'bot':
                return m.author.bot
            elif setting == 'user':
                return not m.author.bot
            elif setting == 'notPinned':
                return not m.pinned
            elif setting == 'userNotPinned':
                return not m.pinned and (not m.author.bot)
            elif setting == 'botNotPinned':
                return not m.pinned and m.author.bot
            elif setting == 'notAdmin':
                return not m.author.guild_permissions.administrator
            elif setting == 'userNotAdmin':
                return not m.author.guild_permissions.administrator and (not m.author.bot)
            elif setting == 'embeds':
                return m.embeds
            elif setting == 'files':
                return m.attachments
            elif setting == 'notAdminNotPinned':
                return not m.author.guild_permissions.administrator and (not m.pinned)
        deleted = await channel.purge(limit=amount, check=check, bulk=True)
        embed = utility.tanjunEmbed(title=locale.commands.admin.purge.success.title(str(command_info.locale)), description=locale.commands.admin.purge.success.description(str(command_info.locale), amount=len(deleted), channel=channel.mention))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.purge.forbidden.title(str(command_info.locale)), description=locale.commands.admin.purge.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.purge.error.title(str(command_info.locale)), description=locale.commands.admin.purge.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
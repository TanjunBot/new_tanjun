from locale_keys import locale
import logging
import re
import aiohttp
import discord
from aiohttp import ClientTimeout
import utility
from utility import EmbedColor

async def copy_emoji(command_info: utility.CommandInfo, emoji: str) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_emojis):
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.copyEmoji.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.copyEmoji.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.manage_emojis:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.copyEmoji.missingPermissionBot.title(command_info.locale), description=locale.commands.admin.copyEmoji.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    emoji_pattern = '<(?:a)?:([^:]+):(\\d+)>'
    matches = list(re.finditer(emoji_pattern, emoji))
    if not matches:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.copyEmoji.error.noEmojis.title(str(command_info.locale)), description=locale.commands.admin.copyEmoji.error.noEmojis.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    successful_emojis = []
    failed_emojis = []
    guild_emojis = command_info.guild.emojis
    animated_count = sum((1 for e in guild_emojis if e.animated))
    static_count = sum((1 for e in guild_emojis if not e.animated))
    animated_limit = command_info.guild.emoji_limit
    static_limit = command_info.guild.emoji_limit
    try:
        for match in matches:
            name = match.group(1)
            emoji_id = int(match.group(2))
            animated = match.group(0).startswith('<a:')
            if animated and animated_count >= animated_limit or (not animated and static_count >= static_limit):
                failed_emojis.append(match.group(0))
                continue
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{('gif' if animated else 'png')}"
            try:
                async with aiohttp.ClientSession() as session, session.get(emoji_url, timeout=ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        failed_emojis.append(match.group(0))
                        continue
                    emoji_bytes = await resp.read()
                new_emoji = await command_info.guild.create_custom_emoji(name=name, image=emoji_bytes, reason=locale.commands.admin.copyEmoji.reason(str(command_info.locale)))
                successful_emojis.append(str(new_emoji))
                if animated:
                    animated_count += 1
                else:
                    static_count += 1
            except Exception:
                logging.exception('Failed to copy emoji %s (id=%s)', name, emoji_id)
                failed_emojis.append(match.group(0))
        if not successful_emojis:
            embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.copyEmoji.error.limitReached.title(command_info.locale), description=locale.commands.admin.copyEmoji.error.limitReached.description(command_info.locale))
        elif len(successful_emojis) == 1 and (not failed_emojis):
            embed = utility.tanjunEmbed(colour=EmbedColor.SUCCESS, title=locale.commands.admin.copyEmoji.success.title(str(command_info.locale)), description=locale.commands.admin.copyEmoji.success.description(command_info.locale, emoji=successful_emojis[0]))
        else:
            description = locale.commands.admin.copyEmoji.success.multiple.description(command_info.locale, emojis=' '.join(successful_emojis), count=len(successful_emojis))
            if failed_emojis:
                description += '\n\n' + locale.commands.admin.copyEmoji.partialSuccess.description(command_info.locale, failed_count=len(failed_emojis), failed_emojis=' '.join(failed_emojis))
            title = locale.commands.admin.copyEmoji.partialSuccess.title(command_info.locale) if failed_emojis else locale.commands.admin.copyEmoji.success.multiple.title(command_info.locale)
            embed = utility.tanjunEmbed(colour=EmbedColor.SUCCESS if not failed_emojis else EmbedColor.WARNING, title=title, description=description)
        await command_info.reply(embed=embed)
    except Exception:
        logging.exception('Unexpected error in copy_emoji command')
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.copyEmoji.error.title(str(command_info.locale)), description=locale.commands.admin.copyEmoji.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
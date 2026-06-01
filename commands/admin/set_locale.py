from locale_keys import locale as l10n
import discord
import utility

async def set_locale(command_info: utility.CommandInfo, locale: str) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_guild):
        embed = utility.tanjunEmbed(title=l10n.commands.admin.setLocale.missingPermission.title(str(command_info.locale)), description=l10n.commands.admin.setLocale.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if command_info.guild is None:
        raise ValueError('Guild is missing in command_info')
    await command_info.guild.edit(preferred_locale=locale, reason=l10n.commands.admin.setLocale.setLocaleReason(str(command_info.locale)))
    embed = utility.tanjunEmbed(title=l10n.commands.admin.setLocale.success.title(str(command_info.locale)), description=l10n.commands.admin.setLocale.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)
    return None
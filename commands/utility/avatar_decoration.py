from locale_keys import locale
import discord
from utility import CommandInfo, tanjunEmbed

async def avatarDecoration(command_info: CommandInfo, user: discord.Member) -> None:
    if not user.avatar_decoration:
        embed = tanjunEmbed(title=locale.commands.utility.avatarDecoration.no_decoration.title(command_info.locale), description=locale.commands.utility.avatarDecoration.no_decoration.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    embed = tanjunEmbed(title=locale.commands.utility.avatarDecoration.title(command_info.locale, user=user.display_name), description=locale.commands.utility.avatarDecoration.description(command_info.locale))
    embed.set_image(url=user.avatar_decoration.url)
    await command_info.reply(embed=embed)
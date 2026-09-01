from locale_keys import locale
import discord
from utility import CommandInfo, tanjunEmbed

async def banner(command_info: CommandInfo, user: discord.User) -> None:
    user = await command_info.client.fetch_user(user.id)
    if not user.banner:
        embed = tanjunEmbed(title=locale.commands.utility.noBanner.title(command_info.locale, user=user.display_name))
        await command_info.reply(embed=embed)
        return
    embed = tanjunEmbed(title=locale.commands.utility.banner.title(command_info.locale, user=user.display_name))
    embed.set_image(url=user.banner.url)
    await command_info.reply(embed=embed)
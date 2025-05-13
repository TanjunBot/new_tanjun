import discord

from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def avatar(commandInfo: commandInfo, user: discord.Member) -> None:
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.avatar.title",
            user=user.display_name,
        ),
    )
    embed.set_image(
        url=user.display_avatar.url
        if user.display_avatar
        else f"https://cdn.discordapp.com/embed/avatars/{(user.id >> 22) % 6}.png"
    )
    if user.guild_avatar and user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    await commandInfo.reply(embed=embed)

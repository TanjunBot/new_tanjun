import discord

from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def banner(commandInfo: commandInfo, user: discord.Member):
    user = await commandInfo.client.fetch_user(user.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.banner.title",
            user=user.display_name,
        ),
    )
    embed.set_image(url=user.banner.url)
    # if user.guild_avatar and user.avatar:
    # embed.set_thumbnail(url=user.avatar.url)
    await commandInfo.reply(embed=embed)

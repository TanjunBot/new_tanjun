import discord

from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def banner(CommandInfo: CommandInfo, user: discord.User) -> None:
    user = await commandInfo.client.fetch_user(user.id)

    if not user.banner:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.noBanner.title",
                user=user.display_name,
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.banner.title",
            user=user.display_name,
        ),
    )
    embed.set_image(url=user.banner.url)
    await commandInfo.reply(embed=embed)

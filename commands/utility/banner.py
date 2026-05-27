import discord

from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def banner(command_info: CommandInfo, user: discord.User) -> None:
    user = await command_info.client.fetch_user(user.id)

    if not user.banner:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.noBanner.title",
                user=user.display_name,
            ),
        )
        await command_info.reply(embed=embed)
        return
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.banner.title",
            user=user.display_name,
        ),
    )
    embed.set_image(url=user.banner.url)
    await command_info.reply(embed=embed)

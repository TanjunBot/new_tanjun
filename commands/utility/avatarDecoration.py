import discord  # type: ignore[import-not-found]

from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def avatarDecoration(commandInfo: CommandInfo, user: discord.Member) -> None:  # type: ignore[no-any-unimported]
    if not user.avatar_decoration:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.avatarDecoration.no_decoration.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.avatarDecoration.no_decoration.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.avatarDecoration.title",
            user=user.display_name,
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.avatarDecoration.description",
        ),
    )
    embed.set_image(url=user.avatar_decoration.url)
    await commandInfo.reply(embed=embed)

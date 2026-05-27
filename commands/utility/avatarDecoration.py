import discord

from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def avatarDecoration(command_info: CommandInfo, user: discord.Member) -> None:
    if not user.avatar_decoration:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.avatarDecoration.no_decoration.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.avatarDecoration.no_decoration.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.avatarDecoration.title",
            user=user.display_name,
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.avatarDecoration.description",
        ),
    )
    embed.set_image(url=user.avatar_decoration.url)
    await command_info.reply(embed=embed)

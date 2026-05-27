import discord

import utility
from localizer import tanjunLocalizer


async def fun_command(
    command_info: utility.CommandInfo,
    fun_type: str,
    member: discord.Member,
    message: str | None,
) -> None:
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            f"commands.fun.{fun_type}.title",
            member=member.name,
            user=command_info.user.name,
        ),
        description=message,
    )
    if fun_type == "poke":
        fun_type = "poking at someone"
    elif fun_type == "wave":
        fun_type = "waving at someone"
    gifs = await utility.getGif(fun_type)
    if gifs:
        embed.set_image(url=gifs[0])
    embed.set_footer(text="Powered By GIPHY")
    await command_info.reply(embed=embed)

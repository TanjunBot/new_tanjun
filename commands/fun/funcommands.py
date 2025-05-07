import discord

import utility
from localizer import tanjunLocalizer


async def fun_command(
    commandInfo: utility.commandInfo,
    fun_type: str,
    member: discord.Member,
    message: str | None,
):
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            f"commands.fun.{fun_type}.title",
            member=member.name,
            user=commandInfo.user.name,
        ),
        description=message,
    )
    if fun_type == "poke":
        fun_type = "poking at someone"
    elif fun_type == "wave":
        fun_type = "waving at someone"
    embed.set_image(url=(await utility.getGif(fun_type))[0])
    embed.set_footer(text="via Tenor")
    await commandInfo.reply(embed=embed)

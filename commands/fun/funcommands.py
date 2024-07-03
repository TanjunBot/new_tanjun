import discord
import utility
from typing import Optional
from localizer import tanjunLocalizer

async def fun_command(commandInfo: utility.commandInfo, fun_type: str, member: discord.Member, message: Optional[str]):
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, f"commands.fun.{fun_type}.title",member=member.name, user=commandInfo.user.name
        ),
        description=message
    )
    embed.set_image(url=(await utility.getGif(fun_type))[0])
    await commandInfo.reply(embed=embed)

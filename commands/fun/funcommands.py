from locale_keys import locale
import discord
import utility

async def fun_command(command_info: utility.CommandInfo, fun_type: str, member: discord.Member, message: str | None) -> None:
    fun_entry = getattr(locale.commands.fun, fun_type)
    embed = utility.tanjunEmbed(title=fun_entry.title(command_info.locale, member=member.name, user=command_info.user.name), description=message)
    if fun_type == 'poke':
        fun_type = 'poking at someone'
    elif fun_type == 'wave':
        fun_type = 'waving at someone'
    gifs = await utility.getGif(fun_type)
    if gifs:
        embed.set_image(url=gifs[0])
    embed.set_footer(text='Powered By GIPHY')
    await command_info.reply(embed=embed)

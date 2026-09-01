from locale_keys import locale
from api import check_if_opted_out, opt_out
from utility import CommandInfo, tanjunEmbed

async def optOut(command_info: CommandInfo) -> None:
    if await check_if_opted_out(command_info.user.id):
        embed = tanjunEmbed(title=locale.commands.utility.messagetrackingoptout.error.title(str(command_info.locale)), description=locale.commands.utility.messagetrackingoptout.error.already_opted_out(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await opt_out(command_info.user.id)
    embed = tanjunEmbed(title=locale.commands.utility.messagetrackingoptout.success.title(str(command_info.locale)), description=locale.commands.utility.messagetrackingoptout.success.description(command_info.locale))
    await command_info.reply(embed=embed)
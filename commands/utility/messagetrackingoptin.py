from locale_keys import locale
from api import check_if_opted_out, opt_in
from utility import CommandInfo, tanjunEmbed

async def optIn(command_info: CommandInfo) -> None:
    if not await check_if_opted_out(command_info.user.id):
        embed = tanjunEmbed(title=locale.commands.utility.messagetrackingoptin.error.title(str(command_info.locale)), description=locale.commands.utility.messagetrackingoptin.error.already_opted_in(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await opt_in(command_info.user.id)
    embed = tanjunEmbed(title=locale.commands.utility.messagetrackingoptin.success.title(str(command_info.locale)), description=locale.commands.utility.messagetrackingoptin.success.description(command_info.locale))
    await command_info.reply(embed=embed)
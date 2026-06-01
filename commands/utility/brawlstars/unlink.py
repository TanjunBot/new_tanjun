from locale_keys import locale
from api import get_brawlstars_linked_account, remove_brawlstars_linked_account
from utility import CommandInfo, tanjunEmbed

async def unlink(command_info: CommandInfo) -> None:
    if not await get_brawlstars_linked_account(command_info.user.id):
        await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.unlink.error.notLinked.title(command_info.locale), description=locale.commands.utility.brawlstars.unlink.error.notLinked.description(command_info.locale)))
        return
    await remove_brawlstars_linked_account(command_info.user.id)
    await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.unlink.success.title(command_info.locale), description=locale.commands.utility.brawlstars.unlink.success.description(command_info.locale)))
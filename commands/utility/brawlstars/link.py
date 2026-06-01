from __future__ import annotations
from locale_keys import locale
from api import add_brawlstars_linked_account, get_brawlstars_linked_account
from services.brawlstars import get_brawlstars_service
from utility import CommandInfo, tanjunEmbed

async def link(command_info: CommandInfo, player_tag: str) -> None:
    if not player_tag.startswith('#'):
        player_tag = f'#{player_tag}'
    service = get_brawlstars_service()
    player_info = await service.get_player(player_tag)
    if not player_info:
        await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.link.error.notFound.title(command_info.locale), description=locale.commands.utility.brawlstars.link.error.notFound.description(command_info.locale)))
        return
    if await get_brawlstars_linked_account(command_info.user.id):
        await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.link.error.alreadyLinked.title(command_info.locale), description=locale.commands.utility.brawlstars.link.error.alreadyLinked.description(command_info.locale)))
        return
    await add_brawlstars_linked_account(command_info.user.id, player_tag)
    await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.link.success.title(command_info.locale), description=locale.commands.utility.brawlstars.link.success.description(command_info.locale, tag=player_tag)))
    return
from __future__ import annotations
from locale_keys import locale
from api import get_brawlstars_linked_account
from services.brawlstars import get_brawlstars_service
from utility import CommandInfo, tanjunEmbed

async def player_info(command_info: CommandInfo, player_tag: str | None=None) -> None:
    if not player_tag:
        player_tag = await get_brawlstars_linked_account(command_info.user.id)
    if player_tag and player_tag.startswith('<@'):
        player_tag_user_id = player_tag.split('<@')[1].split('>')[0]
        player_tag = await get_brawlstars_linked_account(player_tag_user_id)
        if not player_tag:
            await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.battlelog.error.userNotLinked.title(command_info.locale), description=locale.commands.utility.brawlstars.battlelog.error.userNotLinked.description(command_info.locale)))
            return
    if player_tag and (not player_tag.startswith('#')):
        player_tag = f'#{player_tag}'
    if not player_tag:
        await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.playerinfo.error.notLinked.title(command_info.locale), description=locale.commands.utility.brawlstars.playerinfo.error.notLinked.description(command_info.locale)))
        return
    service = get_brawlstars_service()
    player = await service.get_player(player_tag)
    if not player:
        await command_info.reply(locale.commands.utility.brawlstars.playerinfo.error.notFound._text(command_info.locale))
        return
    description = ''
    description += locale.commands.utility.brawlstars.playerinfo.description.trophies(command_info.locale, trophies=player.trophies)
    description += '\n'
    description += locale.commands.utility.brawlstars.playerinfo.description.highest_trophies(command_info.locale, highest_trophies=player.highest_trophies)
    description += '\n'
    description += locale.commands.utility.brawlstars.playerinfo.description.expLevel(command_info.locale, expLevel=player.exp_level)
    if player.club:
        description += '\n'
        description += locale.commands.utility.brawlstars.playerinfo.description.club(command_info.locale, tag=player.club.tag, name=player.club.name)
    description += '\n'
    if player.x3vs3_victories != 0:
        description += locale.commands.utility.brawlstars.playerinfo.description._3v3Victories(command_info.locale, victories=player.x3vs3_victories)
    description += '\n'
    if player.solo_victories != 0:
        description += locale.commands.utility.brawlstars.playerinfo.description.soloVictories(command_info.locale, victories=player.solo_victories)
    description += '\n'
    if player.duo_victories != 0:
        description += locale.commands.utility.brawlstars.playerinfo.description.duoVictories(command_info.locale, victories=player.duo_victories)
    description += '\n'
    description += '\n'
    all_brawlers = await service.get_brawler_list()
    brawlers_count = len(all_brawlers)
    owned_count = len(player.brawlers)
    description += locale.commands.utility.brawlstars.playerinfo.description.brawlers(command_info.locale, brawlers=brawlers_count, owned=owned_count)
    embed = tanjunEmbed(title=locale.commands.utility.brawlstars.playerinfo.title(command_info.locale, player_name=player.name, tag=player_tag), description=description, color=player.name_color or 16777215)
    await command_info.reply(embed=embed)
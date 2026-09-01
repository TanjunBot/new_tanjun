from locale_keys import locale
from locale_keys.nav import field_name
import discord
from api import get_brawlstars_linked_account
from services.brawlstars import get_brawlstars_service
from utility import command_info, date_time_to_timestamp, isoTimeToDate, tanjunEmbed

async def battlelog(command_info: command_info, player_tag: str=None):
    if not player_tag:
        player_tag = await get_brawlstars_linked_account(command_info.user.id)
    if player_tag and player_tag.startswith('<@'):
        player_tag_user_id = player_tag.split('<@')[1].split('>')[0]
        player_tag = await get_brawlstars_linked_account(player_tag_user_id)
        if not player_tag:
            return await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.battlelog.error.userNotLinked.title(command_info.locale), description=locale.commands.utility.brawlstars.battlelog.error.userNotLinked.description(command_info.locale)))
    if player_tag and (not player_tag.startswith('#')):
        player_tag = f'#{player_tag}'
    if not player_tag:
        return await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.battlelog.error.notLinked.title(command_info.locale), description=locale.commands.utility.brawlstars.battlelog.error.notLinked.description(command_info.locale)))
    service = get_brawlstars_service()
    battle_log_items = await service.get_battle_log(player_tag)
    if not battle_log_items:
        await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.brawlstars.battlelog.error.notFound.title(command_info.locale), description=locale.commands.utility.brawlstars.battlelog.error.notFound.description(command_info.locale, tag=player_tag)))
        return
    player_name = ''

    class BattleLogPaginator(discord.ui.View):

        def __init__(self, battles: list, command_info: command_info, player_tag: str, player_name: str):
            super().__init__(timeout=3600)
            self.battles = battles
            self.command_info = command_info
            self.player_tag = player_tag
            self.player_name = player_name
            self.current_page = 0
            self.total_pages = len(battles)

        def generate_page(self, page_num: int) -> discord.Embed:
            item = self.battles[page_num]
            description = ''
            battle_time = isoTimeToDate(item.battle_time)
            battle_time = date_time_to_timestamp(battle_time)
            description += locale.commands.utility.brawlstars.battlelog.description.battle_time(self.command_info.locale, timestamp=battle_time)
            description += '\n'
            game_mode = item.mode
            game_mode_locale = getattr(locale.commands.utility.brawlstars.gameModes, field_name(game_mode))(self.command_info.locale)
            description += locale.commands.utility.brawlstars.battlelog.description.game_mode(self.command_info.locale, game_mode=game_mode_locale)
            description += '\n'
            if item.map:
                map_locale = getattr(locale.commands.utility.brawlstars.maps, field_name(item.map), None)
                if map_locale is not None:
                    map_locale = map_locale(self.command_info.locale)
                else:
                    map_locale = item.map
                description += locale.commands.utility.brawlstars.battlelog.description.game_map(self.command_info.locale, game_map=map_locale)
                description += '\n'
            if item.trophy_change is not None:
                description += locale.commands.utility.brawlstars.battlelog.description.trophy_change(self.command_info.locale, trophy_change=item.trophy_change)
                description += '\n'
            if item.result:
                result_locale = getattr(locale.commands.utility.brawlstars.results, field_name(item.result))(self.command_info.locale)
                description += locale.commands.utility.brawlstars.battlelog.description.result(self.command_info.locale, result=result_locale)
                description += '\n'
            if item.duration is not None:
                description += locale.commands.utility.brawlstars.battlelog.description.duration(self.command_info.locale, duration=item.duration)
                description += '\n'
            if item.star_player:
                sp = item.star_player
                description += locale.commands.utility.brawlstars.battlelog.description.star_player(self.command_info.locale, tag=sp.tag, name=sp.name, brawler_name=sp.brawler.name, brawler_power=sp.brawler.power, brawler_trophies=sp.brawler.trophies)
                description += '\n'
            if item.players:
                description += locale.commands.utility.brawlstars.battlelog.description.enemies(self.command_info.locale)
                for enemie in item.players:
                    tag = enemie.tag
                    if tag.lower() == self.player_tag.lower():
                        self.player_name = enemie.name
                        continue
                    description += locale.commands.utility.brawlstars.battlelog.description.enemy(self.command_info.locale, tag=tag, name=enemie.name, brawler_name=enemie.brawler.name, brawler_power=enemie.brawler.power, brawler_trophies=enemie.brawler.trophies)
                    description += '\n'
            elif item.teams:
                teams = item.teams
                description += locale.commands.utility.brawlstars.battlelog.description.team1(self.command_info.locale)
                for player in teams[0]:
                    description += locale.commands.utility.brawlstars.battlelog.description.teamPlayer(self.command_info.locale, tag=player.tag, name=player.name, brawler_name=player.brawler.name, brawler_power=player.brawler.power, brawler_trophies=player.brawler.trophies)
                    description += '\n'
                description += locale.commands.utility.brawlstars.battlelog.description.team2(self.command_info.locale)
                for player in teams[1]:
                    description += locale.commands.utility.brawlstars.battlelog.description.teamPlayer(self.command_info.locale, tag=player.tag, name=player.name, brawler_name=player.brawler.name, brawler_power=player.brawler.power, brawler_trophies=player.brawler.trophies)
                    description += '\n'
            return tanjunEmbed(title=locale.commands.utility.brawlstars.battlelog.title(self.command_info.locale, player_name=self.player_name, current_page=page_num + 1, total_pages=self.total_pages, tag=self.player_tag), description=description)

        @discord.ui.button(label='⬅️', style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.command_info.user.id:
                await interaction.response.send_message(locale.commands.utility.brawlstars.events.notYourEmbed(self.command_info.locale), ephemeral=True)
                return
            if self.current_page == 0:
                self.current_page = self.total_pages - 1
            else:
                self.current_page -= 1
            await interaction.response.edit_message(view=self, embed=self.generate_page(self.current_page))

        @discord.ui.button(label='➡️', style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.command_info.user.id:
                await interaction.response.send_message(locale.commands.utility.brawlstars.events.notYourEmbed(self.command_info.locale), ephemeral=True)
                return
            if self.current_page == self.total_pages - 1:
                self.current_page = 0
            else:
                self.current_page += 1
            await interaction.response.edit_message(view=self, embed=self.generate_page(self.current_page))
    if len(battle_log_items) > 1:
        view = BattleLogPaginator(battle_log_items, command_info, player_tag, player_name)
        await command_info.reply(embed=view.generate_page(0), view=view)
    else:
        embed = tanjunEmbed(title=locale.commands.utility.brawlstars.battlelog.titleNoPages(command_info.locale, player_name=player_name, tag=player_tag), description='' if not battle_log_items else BattleLogPaginator(battle_log_items, command_info, player_tag, player_name).generate_page(0).description)
        await command_info.reply(embed=embed)
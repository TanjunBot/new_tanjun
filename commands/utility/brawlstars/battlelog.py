import discord

from api import get_brawlstars_linked_account
from localizer import tanjunLocalizer
from services.brawlstars import get_brawlstars_service
from utility import command_info, date_time_to_timestamp, isoTimeToDate, tanjunEmbed


async def battlelog(command_info: command_info, player_tag: str = None):
    if not player_tag:
        player_tag = await get_brawlstars_linked_account(command_info.user.id)
    if player_tag and player_tag.startswith("<@"):
        player_tag_user_id = player_tag.split("<@")[1].split(">")[0]
        player_tag = await get_brawlstars_linked_account(player_tag_user_id)
        if not player_tag:
            return await command_info.reply(
                embed=tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.title",
                    ),
                    description=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.description",
                    ),
                )
            )
    if player_tag and not player_tag.startswith("#"):
        player_tag = f"#{player_tag}"
    if not player_tag:
        return await command_info.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.battlelog.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.battlelog.error.notLinked.description",
                ),
            )
        )

    service = get_brawlstars_service()
    battle_log_items = await service.get_battle_log(player_tag)
    if not battle_log_items:
        await command_info.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.battlelog.error.notFound.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.battlelog.error.notFound.description",
                    tag=player_tag,
                ),
            )
        )
        return

    player_name = ""

    class BattleLogPaginator(discord.ui.View):
        def __init__(
            self,
            battles: list,
            command_info: command_info,
            player_tag: str,
            player_name: str,
        ):
            super().__init__(timeout=3600)
            self.battles = battles
            self.command_info = command_info
            self.player_tag = player_tag
            self.player_name = player_name
            self.current_page = 0
            self.total_pages = len(battles)

        def generate_page(self, page_num: int) -> discord.Embed:
            item = self.battles[page_num]
            description = ""
            battle_time = isoTimeToDate(item.battle_time)
            battle_time = date_time_to_timestamp(battle_time)
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.battle_time",
                timestamp=battle_time,
            )
            description += "\n"
            game_mode = item.mode
            game_mode_locale = tanjunLocalizer.localize(
                self.command_info.locale,
                f"commands.utility.brawlstars.game_modes.{game_mode}",
            )
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.game_mode",
                game_mode=game_mode_locale,
            )
            description += "\n"
            if item.map:
                map_locale = tanjunLocalizer.localize(
                    self.command_info.locale,
                    f"commands.utility.brawlstars.maps.{item.map}",
                )
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.game_map",
                    game_map=map_locale,
                )
                description += "\n"
            if item.trophy_change is not None:
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.trophy_change",
                    trophy_change=item.trophy_change,
                )
                description += "\n"
            if item.result:
                result_locale = tanjunLocalizer.localize(
                    self.command_info.locale,
                    f"commands.utility.brawlstars.results.{item.result}",
                )
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.result",
                    result=result_locale,
                )
                description += "\n"
            if item.duration is not None:
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.duration",
                    duration=item.duration,
                )
                description += "\n"
            if item.star_player:
                sp = item.star_player
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.star_player",
                    tag=sp.tag,
                    name=sp.name,
                    brawler_name=sp.brawler.name,
                    brawler_power=sp.brawler.power,
                    brawler_trophies=sp.brawler.trophies,
                )
                description += "\n"
            if item.players:
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.enemies",
                )
                for enemie in item.players:
                    tag = enemie.tag
                    if tag.lower() == self.player_tag.lower():
                        self.player_name = enemie.name
                        continue
                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.enemy",
                        tag=tag,
                        name=enemie.name,
                        brawler_name=enemie.brawler.name,
                        brawler_power=enemie.brawler.power,
                        brawler_trophies=enemie.brawler.trophies,
                    )
                    description += "\n"
            elif item.teams:
                teams = item.teams
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.team1",
                )
                for player in teams[0]:
                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.teamPlayer",
                        tag=player.tag,
                        name=player.name,
                        brawler_name=player.brawler.name,
                        brawler_power=player.brawler.power,
                        brawler_trophies=player.brawler.trophies,
                    )
                    description += "\n"
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.team2",
                )
                for player in teams[1]:
                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.teamPlayer",
                        tag=player.tag,
                        name=player.name,
                        brawler_name=player.brawler.name,
                        brawler_power=player.brawler.power,
                        brawler_trophies=player.brawler.trophies,
                    )
                    description += "\n"
            return tanjunEmbed(
                title=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.title",
                    player_name=self.player_name,
                    current_page=page_num + 1,
                    total_pages=self.total_pages,
                    tag=self.player_tag,
                ),
                description=description,
            )

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return
            if self.current_page == 0:
                self.current_page = self.total_pages - 1
            else:
                self.current_page -= 1
            await interaction.response.edit_message(view=self, embed=self.generate_page(self.current_page))

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
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
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.battlelog.titleNoPages",
                player_name=player_name,
                tag=player_tag,
            ),
            description=""
            if not battle_log_items
            else BattleLogPaginator(battle_log_items, command_info, player_tag, player_name)
            .generate_page(0)
            .description,
        )
        await command_info.reply(embed=embed)

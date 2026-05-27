import aiohttp
import discord
from aiohttp import ClientTimeout

from api import get_brawlstars_linked_account
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import command_info, date_time_to_timestamp, isoTimeToDate, tanjunEmbed


async def getBattloeLog(player_tag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            f"https://api.brawlstars.com/v1/players/%23{player_tag[1:]}/battlelog",
            headers=headers,
            timeout=ClientTimeout(total=10),
        ) as response,
    ):
        if response.status != 200:
            return None
        return await response.json()


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
    battle_log = await getBattloeLog(player_tag)
    if not battle_log:
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
            battle_log: dict,
            command_info: command_info,
            player_tag: str,
            player_name: str,
        ):
            super().__init__(timeout=3600)
            self.battle_log = battle_log
            self.command_info = command_info
            self.player_tag = player_tag
            self.player_name = player_name
            self.current_page = 0
            self.total_pages = len(battle_log["items"])

        def generate_page(self, page_num: int) -> discord.Embed:
            item = self.battle_log["items"][page_num]
            description = ""
            battle_time = isoTimeToDate(item["battle_time"])
            battle_time = date_time_to_timestamp(battle_time)
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.battle_time",
                timestamp=battle_time,
            )
            description += "\n"
            game_mode = item["event"]["mode"]
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
            game_map = item["event"]["map"]
            map_locale = tanjunLocalizer.localize(
                self.command_info.locale,
                f"commands.utility.brawlstars.maps.{game_map}",
            )
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.game_map",
                game_map=map_locale,
            )
            description += "\n"
            battle = item["battle"]
            trophy_change = battle["trophy_change"]
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.trophy_change",
                trophy_change=trophy_change,
            )
            description += "\n"
            if "result" in battle:
                result = battle["result"]
                result_locale = tanjunLocalizer.localize(
                    self.command_info.locale,
                    f"commands.utility.brawlstars.results.{result}",
                )
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.result",
                    result=result_locale,
                )
                description += "\n"
            if "duration" in battle:
                duration = battle["duration"]
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.duration",
                    duration=duration,
                )
                description += "\n"
            if "star_player" in battle:
                star_player = battle["star_player"]
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.star_player",
                    tag=star_player["tag"],
                    name=star_player["name"],
                    brawler_name=star_player["brawler"]["name"],
                    brawler_power=star_player["brawler"]["power"],
                    brawler_trophies=star_player["brawler"]["trophies"],
                )
                description += "\n"
            if "players" in battle:
                enemies = battle["players"]
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.enemies",
                )
                for enemie in enemies:
                    tag = enemie["tag"]
                    if tag.lower() == self.player_tag.lower():
                        self.player_name = enemie["name"]
                        continue

                    name = enemie["name"]
                    brawler = enemie["brawler"]
                    brawler_name = brawler["name"]
                    brawler_power = brawler["power"]
                    brawler_trophies = brawler["trophies"]

                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.enemy",
                        tag=tag,
                        name=name,
                        brawler_name=brawler_name,
                        brawler_power=brawler_power,
                        brawler_trophies=brawler_trophies,
                    )
                    description += "\n"
            elif "teams" in battle:
                teams = battle["teams"]
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.team1",
                )
                for player in teams[0]:
                    tag = player["tag"]
                    name = player["name"]
                    brawler = player["brawler"]
                    brawler_name = brawler["name"]
                    brawler_power = brawler["power"]
                    brawler_trophies = brawler["trophies"]
                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.teamPlayer",
                        tag=tag,
                        name=name,
                        brawler_name=brawler_name,
                        brawler_power=brawler_power,
                        brawler_trophies=brawler_trophies,
                    )
                    description += "\n"
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.team2",
                )
                for player in teams[1]:
                    tag = player["tag"]
                    name = player["name"]
                    brawler = player["brawler"]
                    brawler_name = brawler["name"]
                    brawler_power = brawler["power"]
                    brawler_trophies = brawler["trophies"]
                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.teamPlayer",
                        tag=tag,
                        name=name,
                        brawler_name=brawler_name,
                        brawler_power=brawler_power,
                        brawler_trophies=brawler_trophies,
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

    if len(battle_log["items"]) > 1:
        view = BattleLogPaginator(battle_log, command_info, player_tag, player_name)
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
            if not battle_log["items"]
            else BattleLogPaginator(battle_log, command_info, player_tag, player_name).generate_page(0).description,
        )
        await command_info.reply(embed=embed)

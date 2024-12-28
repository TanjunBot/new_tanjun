from config import brawlstarsToken
import aiohttp
from utility import commandInfo, tanjunEmbed, isoTimeToDate, date_time_to_timestamp
import discord
from localizer import tanjunLocalizer
from api import get_brawlstars_linked_account


async def getBattloeLog(playerTag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}/battlelog",
            headers=headers,
        ) as response:
            if response.status != 200:
                return None
            return await response.json()


async def battlelog(commandInfo: commandInfo, playerTag: str = None):
    if not playerTag:
        playerTag = await get_brawlstars_linked_account(commandInfo.user.id)
    if playerTag and not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    if not playerTag:
        return await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.battlelog.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.battlelog.error.notLinked.description",
                ),
            )
        )
    battleLog = await getBattloeLog(playerTag)
    if not battleLog:
        await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.battlelog.error.notFound.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.battlelog.error.notFound.description",
                    tag=playerTag,
                ),
            )
        )
        return

    playerName = ""

    class BattleLogPaginator(discord.ui.View):
        def __init__(
            self,
            battle_log: dict,
            command_info: commandInfo,
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
            battleTime = isoTimeToDate(item["battleTime"])
            battleTime = date_time_to_timestamp(battleTime)
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.battleTime",
                timestamp=battleTime,
            )
            description += "\n"
            gameMode = item["event"]["mode"]
            gameModeLocale = tanjunLocalizer.localize(
                self.command_info.locale,
                f"commands.utility.brawlstars.gameModes.{gameMode}",
            )
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.gameMode",
                gameMode=gameModeLocale,
            )
            description += "\n"
            gameMap = item["event"]["map"]
            mapLocale = tanjunLocalizer.localize(
                self.command_info.locale,
                f"commands.utility.brawlstars.maps.{gameMap}",
            )
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.gameMap",
                gameMap=mapLocale,
            )
            description += "\n"
            battle = item["battle"]
            trophyChange = battle["trophyChange"]
            description += tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.brawlstars.battlelog.description.trophyChange",
                trophyChange=trophyChange,
            )
            description += "\n"
            if "result" in battle:
                result = battle["result"]
                resultLocale = tanjunLocalizer.localize(
                    self.command_info.locale,
                    f"commands.utility.brawlstars.results.{result}",
                )
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.result",
                    result=resultLocale,
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
            if "starPlayer" in battle:
                starPlayer = battle["starPlayer"]
                description += tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.description.starPlayer",
                    tag=starPlayer["tag"],
                    name=starPlayer["name"],
                    brawlerName=starPlayer["brawler"]["name"],
                    brawlerPower=starPlayer["brawler"]["power"],
                    brawlerTrophies=starPlayer["brawler"]["trophies"],
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
                    brawlerName = brawler["name"]
                    brawlerPower = brawler["power"]
                    brawlerTrophies = brawler["trophies"]

                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.enemy",
                        tag=tag,
                        name=name,
                        brawlerName=brawlerName,
                        brawlerPower=brawlerPower,
                        brawlerTrophies=brawlerTrophies,
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
                    brawlerName = brawler["name"]
                    brawlerPower = brawler["power"]
                    brawlerTrophies = brawler["trophies"]
                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.teamPlayer",
                        tag=tag,
                        name=name,
                        brawlerName=brawlerName,
                        brawlerPower=brawlerPower,
                        brawlerTrophies=brawlerTrophies,
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
                    brawlerName = brawler["name"]
                    brawlerPower = brawler["power"]
                    brawlerTrophies = brawler["trophies"]
                    description += tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.battlelog.description.teamPlayer",
                        tag=tag,
                        name=name,
                        brawlerName=brawlerName,
                        brawlerPower=brawlerPower,
                        brawlerTrophies=brawlerTrophies,
                    )
                    description += "\n"
            return tanjunEmbed(
                title=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.brawlstars.battlelog.title",
                    playerName=self.player_name,
                    current_page=page_num + 1,
                    total_pages=self.total_pages,
                    tag=self.player_tag,
                ),
                description=description,
            )

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if not interaction.user.id == self.command_info.user.id:
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
            await interaction.response.edit_message(
                view=self, embed=self.generate_page(self.current_page)
            )

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if not interaction.user.id == self.command_info.user.id:
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
            await interaction.response.edit_message(
                view=self, embed=self.generate_page(self.current_page)
            )

    if len(battleLog["items"]) > 1:
        view = BattleLogPaginator(battleLog, commandInfo, playerTag, playerName)
        await commandInfo.reply(embed=view.generate_page(0), view=view)
    else:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.battlelog.titleNoPages",
                playerName=playerName,
                tag=playerTag,
            ),
            description="" if not battleLog["items"] else BattleLogPaginator(battleLog, commandInfo, playerTag, playerName).generate_page(0).description
        )
        await commandInfo.reply(embed=embed)

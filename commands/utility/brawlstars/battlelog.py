from config import brawlstarsToken
import aiohttp
from utility import commandInfo, tanjunEmbed, isoTimeToDate, date_time_to_timestamp
import discord
from localizer import tanjunLocalizer


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


async def battlelog(commandInfo: commandInfo, playerTag: str):
    if not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
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

    pages = []

    playerName = ""

    for item in battleLog["items"]:
        description = ""
        battleTime = isoTimeToDate(item["battleTime"])
        battleTime = date_time_to_timestamp(battleTime)
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.battlelog.description.battleTime",
            timestamp=battleTime,
        )
        description += "\n"
        gameMode = item["event"]["mode"]
        gameModeLocale = tanjunLocalizer.localize(
            commandInfo.locale,
            f"commands.utility.brawlstars.gameModes.{gameMode}",
        )
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.battlelog.description.gameMode",
            gameMode=gameModeLocale,
        )
        description += "\n"
        gameMap = item["event"]["map"]
        mapLocale = tanjunLocalizer.localize(
            commandInfo.locale,
            f"commands.utility.brawlstars.maps.{gameMap}",
        )
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.battlelog.description.gameMap",
            gameMap=mapLocale,
        )
        description += "\n"
        battle = item["battle"]
        trophyChange = battle["trophyChange"]
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.battlelog.description.trophyChange",
            trophyChange=trophyChange,
        )
        description += "\n"
        if "result" in battle:
            result = battle["result"]
            resultLocale = tanjunLocalizer.localize(
                commandInfo.locale,
                f"commands.utility.brawlstars.results.{result}",
            )
            description += tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.battlelog.description.result",
                result=resultLocale,
            )
            description += "\n"
        if "duration" in battle:
            duration = battle["duration"]
            description += tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.battlelog.description.duration",
                duration=duration,
            )
            description += "\n"
        if "starPlayer" in battle:
            starPlayer = battle["starPlayer"]
            description += tanjunLocalizer.localize(
                commandInfo.locale,
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
                commandInfo.locale,
                "commands.utility.brawlstars.battlelog.description.enemies",
            )
            for enemie in enemies:
                tag = enemie["tag"]
                if tag.lower() == playerTag.lower():
                    playerName = enemie["name"]
                    continue

                name = enemie["name"]
                brawler = enemie["brawler"]
                brawlerName = brawler["name"]
                brawlerPower = brawler["power"]
                brawlerTrophies = brawler["trophies"]

                description += tanjunLocalizer.localize(
                    commandInfo.locale,
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
                commandInfo.locale,
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
                    commandInfo.locale,
                    "commands.utility.brawlstars.battlelog.description.teamPlayer",
                    tag=tag,
                    name=name,
                    brawlerName=brawlerName,
                    brawlerPower=brawlerPower,
                    brawlerTrophies=brawlerTrophies,
                )
                description += "\n"
            description += tanjunLocalizer.localize(
                commandInfo.locale,
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
                    commandInfo.locale,
                    "commands.utility.brawlstars.battlelog.description.teamPlayer",
                    tag=tag,
                    name=name,
                    brawlerName=brawlerName,
                    brawlerPower=brawlerPower,
                    brawlerTrophies=brawlerTrophies,
                )
                description += "\n"
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.battlelog.title",
                playerName=playerName,
                current_page=len(pages) + 1,
                total_pages=len(battleLog["items"]),
                tag=playerTag,
            ),
            description=description,
        )
        pages.append(embed)

    class BattleLogPaginator(discord.ui.View):
        def __init__(self, pages: list[tanjunEmbed]):
            super().__init__(timeout=3600)
            self.pages = pages
            self.current_page = 0

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return
            if self.current_page == 0:
                self.current_page = len(self.pages) - 1
            else:
                self.current_page -= 1
            await interaction.response.edit_message(
                view=self, embed=pages[self.current_page]
            )

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return
            if self.current_page == len(self.pages) - 1:
                self.current_page = 0
            else:
                self.current_page += 1
            await interaction.response.edit_message(
                view=self, embed=pages[self.current_page]
            )

    if len(pages) > 1:
        view = BattleLogPaginator(pages)
        await commandInfo.reply(embed=pages[0], view=view)
    else:

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.battlelog.titleNoPages",
                playerName=playerName,
                tag=playerTag,
            ),
            description=pages[0].description,
        )
        await commandInfo.reply(embed=embed)

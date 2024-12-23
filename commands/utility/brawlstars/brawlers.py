from config import brawlstarsToken
import aiohttp
from utility import commandInfo, tanjunEmbed, similar
import discord
from localizer import tanjunLocalizer
import json
from commands.utility.brawlstars.bshelper import (
    parseName,
    getGadgetEmoji,
    getStarPowerEmoji,
    getGearEmoji,
)


async def getPlayerInfo(playerTag: str):
    print("token", brawlstarsToken)
    print("gettin", playerTag)
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}",
            headers=headers,
        ) as response:
            print(response.status)
            if response.status != 200:
                respo = await response.json()
                print(respo)
                return None
            return await response.json()


async def brawlers(commandInfo: commandInfo, playerTag: str):
    if not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    playerInfo = await getPlayerInfo(playerTag)
    if not playerInfo:
        return await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.error.notFound",
            )
        )

    playerName = playerInfo["name"]

    pages = []
    for brawler in playerInfo["brawlers"]:
        id = brawler["id"]
        name = parseName(brawler["name"])
        power = brawler["power"]
        rank = brawler["rank"]
        trophies = brawler["trophies"]
        highestTrophies = brawler["highestTrophies"]
        gears = brawler["gears"]
        gadgets = brawler["gadgets"]
        starPowers = brawler["starPowers"]

        description = tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.brawlers.description.overview",
            name=name,
            power=power,
            rank=rank,
            trophies=trophies,
            highestTrophies=highestTrophies,
        )
        description += "\n"

        if len(starPowers) > 0:
            description += tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.description.starPowers",
            )
            description += "\n"

            for starPower in starPowers:
                name = f" {getStarPowerEmoji(starPower['id'])} {parseName(starPower['name'])}"
                description += tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.brawlers.description.starPower",
                    name=name,
                )
                description += "\n"
            description += "\n"

        if len(gadgets) > 0:
            description += tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.description.gadgets",
            )
            description += "\n"

            for gadget in gadgets:
                name = f" {getGadgetEmoji(gadget['id'])} {parseName(gadget['name'])}"
                description += tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.brawlers.description.gadget",
                    name=name,
                )
                description += "\n"
            description += "\n"

        if len(gears) > 0:
            description += tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.description.gears",
            )
            description += "\n"

            for gear in gears:
                name = f" {getGearEmoji(gear['id'])} {parseName(gear['name'])}"
                description += tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.brawlers.description.gear",
                    name=name,
                    level=gear["level"],
                )
                description += "\n"
            description += "\n"
            
        description += "\n"
        description += f"raw:\n```json\n{json.dumps(brawler, indent=4)}\n```"

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.title",
                current_page=len(pages) + 1,
                total_pages=len(playerInfo["brawlers"]),
                name=playerName,
                tag=playerTag,
            ),
            description=description,
        )
        embed.set_thumbnail(
            url=f"https://cdn.brawlify.com/brawlers/borderless/{id}.png"
        )
        pages.append(embed)

    class BrawlersPaginator(discord.ui.View):
        def __init__(self, pages: list[tanjunEmbed], current_page=0):
            super().__init__(timeout=3600)
            self.pages = pages
            self.current_page = current_page

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
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
            if self.current_page == len(self.pages) - 1:
                self.current_page = 0
            else:
                self.current_page += 1
            await interaction.response.edit_message(
                view=self, embed=pages[self.current_page]
            )

        @discord.ui.button(label="🔍", style=discord.ButtonStyle.primary)
        async def search(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(SearchModal(commandInfo))

    class SearchModal(discord.ui.Modal):
        def __init__(self, commandInfo: commandInfo):
            super().__init__(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.brawlers.search.title",
                )
            )
            self.commandInfo = commandInfo
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.placeholder",
                    ),
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            try:
                brawlerName = self.children[0].value

                desiredPage = 0
                bestSimilarity = -100
                for i, brawler in enumerate(playerInfo["brawlers"]):
                    similarity = similar(brawler["name"].lower(), brawlerName.lower())
                    if similarity > bestSimilarity:
                        bestSimilarity = similarity
                        desiredPage = i

                view = BrawlersPaginator(pages, desiredPage)
                page = pages[desiredPage]
                await interaction.response.edit_message(view=view, embed=page)

            except ValueError:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    if len(pages) > 1:
        view = BrawlersPaginator(pages)
        await commandInfo.reply(embed=pages[0], view=view)
    else:

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.titleNoPages",
                playerName=playerName,
                tag=playerTag,
            ),
            description=pages[0].description,
        )
        await commandInfo.reply(embed=embed)

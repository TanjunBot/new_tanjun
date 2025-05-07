import json

import aiohttp
import discord

from api import get_brawlstars_linked_account
from commands.utility.brawlstars.bshelper import (
    getGadgetEmoji,
    getGearEmoji,
    getLevelEmoji,
    getStarPowerEmoji,
    parseName,
)
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import commandInfo, similar, tanjunEmbed


async def getPlayerInfo(playerTag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}",
            headers=headers,
        ) as response:
            if response.status != 200:
                return None
            return await response.json()


async def brawlers(commandInfo: commandInfo, playerTag: str = None):
    if not playerTag:
        playerTag = await get_brawlstars_linked_account(commandInfo.user.id)
    if playerTag and playerTag.startswith("<@"):
        playerTagUserID = playerTag.split("<@")[1].split(">")[0]
        playerTag = await get_brawlstars_linked_account(playerTagUserID)
        if not playerTag:
            return await commandInfo.reply(
                embed=tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.title",
                    ),
                    description=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.description",
                    ),
                )
            )
    if playerTag and not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    if not playerTag:
        return await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.brawlers.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.brawlers.error.notLinked.description",
                ),
            )
        )
    playerInfo = await getPlayerInfo(playerTag)
    if not playerInfo:
        return await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.error.notFound",
            )
        )

    playerName = playerInfo["name"]
    total_brawlers = len(playerInfo["brawlers"])

    async def generate_page(page_number: int) -> discord.Embed:
        brawler = playerInfo["brawlers"][page_number]
        id = brawler["id"]
        name = parseName(brawler["name"])
        power = brawler["power"]
        rank = brawler["rank"]
        trophies = brawler["trophies"]
        highestTrophies = brawler["highestTrophies"]
        gears = brawler["gears"]
        gadgets = brawler["gadgets"]
        starPowers = brawler["starPowers"]
        levelEmoji = getLevelEmoji(rank)

        if rank <= 50:
            description = tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.description.overview",
                name=name,
                power=power,
                rank=rank,
                trophies=trophies,
                highestTrophies=highestTrophies,
                levelEmoji=levelEmoji,
            )
            description += "\n"
        else:
            description = tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.description.overviewMaxTier",
                name=name,
                power=power,
                rank=rank,
                trophies=trophies,
                highestTrophies=highestTrophies,
                levelEmoji=levelEmoji,
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
                )
                description += "\n"
            description += "\n"
            description += "\n"

        if commandInfo.user.id == 1295625022454370346 and commandInfo.guild.id == 947219439764521060:
            description += "\n"
            description += f"raw: \n```json\n{json.dumps(brawler, indent=4)}\n```"

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.title",
                current_page=page_number + 1,
                total_pages=total_brawlers,
                name=playerName,
                tag=playerTag,
            ),
            description=description,
        )
        embed.set_thumbnail(url=f"https://cdn.brawlify.com/brawlers/borderless/{id}.png")
        return embed

    class BrawlersPaginator(discord.ui.View):
        def __init__(self, current_page=0):
            super().__init__(timeout=3600)
            self.current_page = current_page

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
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
                self.current_page = total_brawlers - 1
            else:
                self.current_page -= 1

            new_page = await generate_page(self.current_page)
            await interaction.response.edit_message(view=self, embed=new_page)

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return

            if self.current_page == total_brawlers - 1:
                self.current_page = 0
            else:
                self.current_page += 1

            new_page = await generate_page(self.current_page)
            await interaction.response.edit_message(view=self, embed=new_page)

        @discord.ui.button(label="🔍", style=discord.ButtonStyle.primary)
        async def search(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return
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

                view = BrawlersPaginator(desiredPage)
                page = await generate_page(desiredPage)
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

            except Exception:
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

    if total_brawlers > 1:
        first_page = await generate_page(0)
        view = BrawlersPaginator()
        await commandInfo.reply(embed=first_page, view=view)
    else:
        first_page = await generate_page(0)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.brawlers.titleNoPages",
                playerName=playerName,
                tag=playerTag,
            ),
            description=first_page.description,
        )
        await commandInfo.reply(embed=embed)

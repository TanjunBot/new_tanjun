from config import brawlstarsToken
import aiohttp
from utility import commandInfo, tanjunEmbed, similar, isoTimeToDate, date_time_to_timestamp
import discord
from localizer import tanjunLocalizer
import json
from commands.utility.brawlstars.bshelper import (
    parseName,
    getGadgetEmoji,
    getStarPowerEmoji,
    getGearEmoji,
)


async def getEventRotation():
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/events/rotation",
            headers=headers,
        ) as response:
            if response.status != 200:
                respo = await response.json()
                return None
            return await response.json()


async def events(commandInfo: commandInfo):
    eventRotation = await getEventRotation()
    if not eventRotation:
        return await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.events.error.notFound",
            )
        )

    pages = []
    for event in eventRotation:
        startTime = event["startTime"]
        startTimestamp = date_time_to_timestamp(isoTimeToDate(startTime))
        endTime = event["endTime"]
        endTimestamp = date_time_to_timestamp(isoTimeToDate(endTime))
        map_ = event["event"]["map"]
        mapLocale = tanjunLocalizer.localize(
            commandInfo.locale,
            f"commands.utility.brawlstars.maps.{map_}",
        )
        mode = event["event"]["mode"]
        modeLocale = tanjunLocalizer.localize(
            commandInfo.locale,
            f"commands.utility.brawlstars.gameModes.{mode}",
        )

        description = tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.events.description",
            startTime=startTimestamp,
            endTime=endTimestamp,
            map_=mapLocale,
            mode=modeLocale,
        )

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.events.title",
                current_page=len(pages) + 1,
                total_pages=len(eventRotation),
            ),
            description=description,
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

    if len(pages) > 1:
        view = BrawlersPaginator(pages)
        await commandInfo.reply(embed=pages[0], view=view)
    else:

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.events.titleNoPages",
            ),
            description=pages[0].description,
        )
        await commandInfo.reply(embed=embed)

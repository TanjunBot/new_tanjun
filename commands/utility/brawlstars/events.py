import aiohttp
import discord

from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import (
    commandInfo,
    date_time_to_timestamp,
    isoTimeToDate,
    tanjunEmbed,
)


async def getEventRotation():
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.brawlstars.com/v1/events/rotation",
            headers=headers,
        ) as response:
            if response.status != 200:
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

    async def generate_page(page_num: int) -> discord.Embed:
        event = eventRotation[page_num]
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

        return tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.events.title",
                current_page=page_num + 1,
                total_pages=len(eventRotation),
            ),
            description=description,
        )

    class BrawlersPaginator(discord.ui.View):
        def __init__(self, total_pages: int, current_page=0):
            super().__init__(timeout=3600)
            self.total_pages = total_pages
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
                self.current_page = self.total_pages - 1
            else:
                self.current_page -= 1
            await interaction.response.edit_message(view=self, embed=await generate_page(self.current_page))

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
            if self.current_page == self.total_pages - 1:
                self.current_page = 0
            else:
                self.current_page += 1
            await interaction.response.edit_message(view=self, embed=await generate_page(self.current_page))

    if len(eventRotation) > 1:
        view = BrawlersPaginator(len(eventRotation))
        await commandInfo.reply(embed=await generate_page(0), view=view)
    else:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.events.titleNoPages",
            ),
            description=(await generate_page(0)).description,
        )
        await commandInfo.reply(embed=embed)

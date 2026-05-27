import aiohttp
import discord
from aiohttp import ClientTimeout

from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import (
    command_info,
    date_time_to_timestamp,
    isoTimeToDate,
    tanjunEmbed,
)


async def getEventRotation():
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            "https://api.brawlstars.com/v1/events/rotation",
            headers=headers,
            timeout=ClientTimeout(total=10),
        ) as response,
    ):
        if response.status != 200:
            return None
        return await response.json()


async def events(command_info: command_info):
    event_rotation = await getEventRotation()
    if not event_rotation:
        return await command_info.reply(
            tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.events.error.notFound",
            )
        )

    async def generate_page(page_num: int) -> discord.Embed:
        event = event_rotation[page_num]
        start_time = event["start_time"]
        start_timestamp = date_time_to_timestamp(isoTimeToDate(start_time))
        end_time = event["end_time"]
        end_timestamp = date_time_to_timestamp(isoTimeToDate(end_time))
        map_ = event["event"]["map"]
        map_locale = tanjunLocalizer.localize(
            command_info.locale,
            f"commands.utility.brawlstars.maps.{map_}",
        )
        mode = event["event"]["mode"]
        mode_locale = tanjunLocalizer.localize(
            command_info.locale,
            f"commands.utility.brawlstars.game_modes.{mode}",
        )

        description = tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.events.description",
            start_time=start_timestamp,
            end_time=end_timestamp,
            map_=map_locale,
            mode=mode_locale,
        )

        return tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.events.title",
                current_page=page_num + 1,
                total_pages=len(event_rotation),
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
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        command_info.locale,
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
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        command_info.locale,
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

    if len(event_rotation) > 1:
        view = BrawlersPaginator(len(event_rotation))
        await command_info.reply(embed=await generate_page(0), view=view)
    else:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.events.titleNoPages",
            ),
            description=(await generate_page(0)).description,
        )
        await command_info.reply(embed=embed)

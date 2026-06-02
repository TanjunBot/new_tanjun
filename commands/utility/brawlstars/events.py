from locale_keys import locale
from locale_keys.nav import field_name
import discord
from services.brawlstars import get_brawlstars_service
from utility import command_info, date_time_to_timestamp, isoTimeToDate, tanjunEmbed

async def events(command_info: command_info):
    service = get_brawlstars_service()
    event_rotation = await service.get_events()
    if not event_rotation:
        return await command_info.reply(locale.commands.utility.brawlstars.events.error.notFound(command_info.locale))

    async def generate_page(page_num: int) -> discord.Embed:
        event = event_rotation[page_num]
        start_time = event.start_time
        start_timestamp = date_time_to_timestamp(isoTimeToDate(start_time))
        end_time = event.end_time
        end_timestamp = date_time_to_timestamp(isoTimeToDate(end_time))
        map_ = event.event.map
        map_locale = getattr(locale.commands.utility.brawlstars.maps, field_name(map_), None)
        if map_locale is not None:
            map_locale = map_locale(command_info.locale)
        else:
            map_locale = map_
        mode = event.event.mode
        mode_locale = getattr(locale.commands.utility.brawlstars.gameModes, field_name(mode))(command_info.locale)
        description = locale.commands.utility.brawlstars.events.description(command_info.locale, start_time=start_timestamp, end_time=end_timestamp, map_=map_locale, mode=mode_locale)
        return tanjunEmbed(title=locale.commands.utility.brawlstars.events.title(command_info.locale, current_page=page_num + 1, total_pages=len(event_rotation)), description=description)

    class BrawlersPaginator(discord.ui.View):

        def __init__(self, total_pages: int, current_page=0):
            super().__init__(timeout=3600)
            self.total_pages = total_pages
            self.current_page = current_page

        @discord.ui.button(label='⬅️', style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.utility.brawlstars.events.notYourEmbed(command_info.locale), ephemeral=True)
                return
            if self.current_page == 0:
                self.current_page = self.total_pages - 1
            else:
                self.current_page -= 1
            await interaction.response.edit_message(view=self, embed=await generate_page(self.current_page))

        @discord.ui.button(label='➡️', style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.utility.brawlstars.events.notYourEmbed(command_info.locale), ephemeral=True)
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
        embed = tanjunEmbed(title=locale.commands.utility.brawlstars.events.titleNoPages(command_info.locale), description=(await generate_page(0)).description)
        await command_info.reply(embed=embed)
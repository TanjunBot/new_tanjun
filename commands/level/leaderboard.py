import discord

import utility
from api import (
    get_custom_formula,
    get_level_leaderboard_count,
    get_level_leaderboard_paginated,
    get_xp_scaling,
)
from localizer import tanjunLocalizer

ITEMS_PER_PAGE = 10


async def leaderboard(commandInfo: utility.commandInfo, page: int = 1):
    if page < 1:
        page = 1

    total_entries = await get_level_leaderboard_count(commandInfo.guild.id)
    if total_entries == 0:
        await commandInfo.message.channel.send(
            tanjunLocalizer.localize(commandInfo.locale, "commands.level.leaderboard.no_data")
        )
        return

    total_pages = max(1, (total_entries + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    if page > total_pages:
        page = total_pages

    scaling = await get_xp_scaling(commandInfo.guild.id)
    custom_formula = await get_custom_formula(commandInfo.guild.id)

    async def load_page(page_number: int) -> list:
        offset = (page_number - 1) * ITEMS_PER_PAGE
        return await get_level_leaderboard_paginated(
            commandInfo.guild.id,
            limit=ITEMS_PER_PAGE,
            offset=offset,
        )

    async def generate_page(page_number: int) -> discord.Embed:
        entries = await load_page(page_number)
        description = ""
        base_rank = (page_number - 1) * ITEMS_PER_PAGE + 1
        for i, entry in enumerate(entries):
            user = entry.user_id
            xp = entry.xp
            level = utility.get_level_for_xp(xp, scaling, custom_formula)
            xp_from_last_level = xp - utility.get_xp_for_level(level - 1, scaling, custom_formula)
            xp_till_next_level = utility.get_xp_for_level(level, scaling, custom_formula)
            description += (
                f"\n{base_rank + i}. <@{user}> - "
                f"{tanjunLocalizer.localize(commandInfo.locale, 'commands.level.leaderboard.data', level=level, xp_from_last_level=xp_from_last_level, xp_till_next_level=xp_till_next_level)}"
            )

        if total_pages > 1:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.level.leaderboard.title",
                    current_page=page_number,
                    total_pages=total_pages,
                ),
                description=description,
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.level.leaderboard.titleNoPages"),
                description=description,
            )
        return embed

    class LeaderboardPaginator(discord.ui.View):
        def __init__(self, current_page=1):
            super().__init__(timeout=3600)
            self.current_page = current_page
            self.total_pages = total_pages

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.level.leaderboard.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return

            if self.current_page == 1:
                self.current_page = self.total_pages
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
                        "commands.level.leaderboard.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return

            if self.current_page == self.total_pages:
                self.current_page = 1
            else:
                self.current_page += 1

            new_page = await generate_page(self.current_page)
            await interaction.response.edit_message(view=self, embed=new_page)

    first_page = await generate_page(page)
    view = LeaderboardPaginator(page)
    await commandInfo.reply(embed=first_page, view=view)

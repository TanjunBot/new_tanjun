from typing import Any, cast

import discord  # type: ignore[import-not-found]

import utility
from api import get_custom_formula, get_xp_scaling, getLevelLeaderboard
from localizer import tanjunLocalizer


async def leaderboard(commandInfo: utility.CommandInfo, page: int = 1) -> None:
    if page < 1:
        page = 1
    assert commandInfo.guild is not None
    leaderboard_data = cast(list[tuple[int, int]], await getLevelLeaderboard(commandInfo.guild.id))
    scaling = str(await get_xp_scaling(commandInfo.guild.id))
    custom_formula = str(await get_custom_formula(commandInfo.guild.id))
    if not leaderboard_data:
        await commandInfo.reply(
            content=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.leaderboard.no_data")
        )
        return
    if len(leaderboard_data) == 0:
        await commandInfo.reply(
            content=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.leaderboard.no_data")
        )
        return
    if page > len(leaderboard_data) / 10 + 1:
        page = int(len(leaderboard_data) / 10 + 1)

    async def generate_page(page_number: int) -> discord.Embed:  # type: ignore[no-any-unimported]
        description = ""
        for i in range(10):
            try:
                placeData = leaderboard_data[i + (page_number - 1) * 10]
                user_id = str(placeData[0])
                xp = int(placeData[1])
                level = utility.get_level_for_xp(xp, scaling, custom_formula)
                xp_from_last_level = xp - utility.get_xp_for_level(level - 1, scaling, custom_formula)
                xp_till_next_level = utility.get_xp_for_level(level, scaling, custom_formula)
                description += f"\n{i + 1 + (page_number - 1) * 10}. <@{user_id}> - {tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.leaderboard.data', level=level, xp_from_last_level=xp_from_last_level, xp_till_next_level=xp_till_next_level)}"
            except (IndexError, KeyError):
                break

        total_pages = int(len(leaderboard_data) / 10 + 1)
        if total_pages > 1:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    str(commandInfo.locale),
                    "commands.level.leaderboard.title",
                    current_page=page_number,
                    total_pages=total_pages,
                ),
                description=description,
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.leaderboard.titleNoPages"),
                description=description,
            )
        return embed

    class LeaderboardPaginator(discord.ui.View):  # type: ignore[misc,no-any-unimported]
        def __init__(self, current_page: int = 1) -> None:
            super().__init__(timeout=3600)
            self.current_page = current_page
            leaderboard_len: int = len(leaderboard_data)
            self.total_pages = int(leaderboard_len / 10 + 1)

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)  # type: ignore[untyped-decorator]
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            if not interaction.user.id == CommandInfo.user.id:  # type: ignore[name-defined]
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

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)  # type: ignore[untyped-decorator]
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            if not interaction.user.id == CommandInfo.user.id:  # type: ignore[name-defined]
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

import discord

import utility
from api import get_custom_formula, get_xp_scaling, getLevelLeaderboard
from localizer import tanjunLocalizer


async def leaderboard(commandInfo: utility.commandInfo, page: int = 1):
    if page < 1:
        page = 1
    leaderboard = await getLevelLeaderboard(commandInfo.guild.id)
    scaling = await get_xp_scaling(commandInfo.guild.id)
    custom_formula = await get_custom_formula(commandInfo.guild.id)
    if not leaderboard:
        await commandInfo.message.channel.send(
            tanjunLocalizer.localize(commandInfo.locale, "commands.level.leaderboard.no_data")
        )
        return
    if len(leaderboard) == 0:
        await commandInfo.message.channel.send(
            tanjunLocalizer.localize(commandInfo.locale, "commands.level.leaderboard.no_data")
        )
        return
    if page > len(leaderboard) / 10 + 1:
        page = int(len(leaderboard) / 10 + 1)

    async def generate_page(page_number: int) -> discord.Embed:
        description = ""
        for i in range(10):
            try:
                placeData = leaderboard[i + (page_number - 1) * 10]
                user = placeData[0]
                xp = placeData[1]
                level = utility.get_level_for_xp(xp, scaling, custom_formula)
                xp_from_last_level = xp - utility.get_xp_for_level(level - 1, scaling, custom_formula)
                xp_till_next_level = utility.get_xp_for_level(level, scaling, custom_formula)
                description += f"\n{i + 1 + (page_number - 1) * 10}. <@{user}> - {tanjunLocalizer.localize(commandInfo.locale, 'commands.level.leaderboard.data', level=level, xp_from_last_level=xp_from_last_level, xp_till_next_level=xp_till_next_level)}"
            except Exception:
                break

        if int(len(leaderboard) / 10 + 1) > 1:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.level.leaderboard.title",
                    current_page=page_number,
                    total_pages=int(len(leaderboard) / 10 + 1),
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
            self.total_pages = int(len(leaderboard) / 10 + 1)

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

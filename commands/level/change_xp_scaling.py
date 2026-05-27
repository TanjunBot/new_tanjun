import math

import discord
from discord.ui import Button, View

from api import get_custom_formula, set_custom_formula, set_xp_scaling
from localizer import tanjunLocalizer
from utility import (
    LEVEL_SCALINGS,
    command_info,
    get_xp_for_level,
    tanjunEmbed,
)


class PaginationView(View):
    def __init__(self, generate_page, command_info, total_pages):
        super().__init__(timeout=60)
        self.generate_page = generate_page
        self.current_page = 0
        self.command_info = command_info
        self.total_pages = total_pages

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.gray, disabled=True)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = max(0, self.current_page - 1)
        await self.update_message(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1

        await interaction.response.edit_message(embed=await self.generate_page(self.current_page), view=self)


async def change_xp_scaling_command(command_info: command_info, scaling: str, custom_formula: str = None):
    if custom_formula:
        custom_formula = custom_formula.replace("x", "level")
    if not command_info.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.changexpscaling.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.changexpscaling.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if scaling == "custom" and not custom_formula:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.changexpscaling.error.no_custom_formula.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.changexpscaling.error.no_custom_formula.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if scaling not in LEVEL_SCALINGS and scaling != "custom":
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.changexpscaling.error.invalid_scaling.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.changexpscaling.error.invalid_scaling.description",
                available_scalings=", ".join(list(LEVEL_SCALINGS.keys()) + ["custom"]),
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_xp_scaling(str(command_info.guild.id), scaling)
    if scaling == "custom":
        await set_custom_formula(str(command_info.guild.id), custom_formula)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.level.changexpscaling.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.level.changexpscaling.success.description",
            scaling=scaling,
            formula=(
                custom_formula
                if scaling == "custom"
                else tanjunLocalizer.localize(
                    command_info.locale,
                    f"commands.level.changexpscaling.formulas.{scaling}",
                )
            ),
        ),
    )

    # Add field to show XP required for first 5 levels
    xp_examples = "\n".join([f"Level {i}: {get_xp_for_level(i, scaling, custom_formula)} XP" for i in range(1, 6)])
    embed.add_field(
        name=tanjunLocalizer.localize(command_info.locale, "commands.level.changexpscaling.xp_examples"),
        value=xp_examples,
        inline=False,
    )

    await command_info.reply(embed=embed)


async def show_xp_scalings(command_info: command_info, start_level: int = 1, end_level: int = 5):
    if start_level > end_level:
        start_level, end_level = end_level, start_level

    levels_per_page = 15
    total_pages = math.ceil((end_level - start_level + 1) / levels_per_page)

    async def generatePage(page: int):
        if page >= total_pages:
            page = total_pages - 1
        current_start = start_level + page * levels_per_page
        current_end = min(current_start + levels_per_page - 1, end_level)

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(command_info.locale, "commands.level.showxpscalings.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.showxpscalings.description",
                start_level=current_start,
                end_level=current_end,
            ),
        )

        for scaling in list(LEVEL_SCALINGS.keys()) + ["custom"]:
            if scaling == "custom":
                custom_formula = await get_custom_formula(str(command_info.guild.id))
                if not custom_formula:
                    continue
                formula_display = custom_formula
            else:
                formula_display = tanjunLocalizer.localize(
                    command_info.locale,
                    f"commands.level.changexpscaling.formulas.{scaling}",
                )

            xp_examples = "\n".join(
                [
                    tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.level.showxpscalings.data",
                        level=i,
                        xp=get_xp_for_level(i, scaling, custom_formula if scaling == "custom" else None),
                    )
                    for i in range(current_start, current_end + 1)
                ]
            )

            field_content = f"{formula_display}\n{xp_examples}"

            embed.add_field(
                name=tanjunLocalizer.localize(
                    command_info.locale,
                    f"commands.level.changexpscaling.scalings.{scaling}",
                ),
                value=field_content,
                inline=False,
            )

        return embed

    if total_pages == 1:
        await command_info.reply(embed=await generatePage(0))
    else:
        view = PaginationView(generatePage, command_info, total_pages)
        message = await command_info.reply(embed=await generatePage(0), view=view)
        view.message = message

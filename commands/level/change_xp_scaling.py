from utility import (
    commandInfo,
    tanjunEmbed,
    checkIfHasPro,
    LEVEL_SCALINGS,
    get_xp_for_level,
)
from localizer import tanjunLocalizer
from api import set_xp_scaling, set_custom_formula, get_custom_formula
import discord
from discord.ui import View, Button
import math


class PaginationView(View):
    def __init__(self, pages, commandInfo):
        super().__init__(timeout=60)
        self.pages = pages
        self.current_page = 0
        self.commandInfo = commandInfo

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray, disabled=True)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = max(0, self.current_page - 1)
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = min(len(self.pages) - 1, self.current_page + 1)
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1

        await interaction.response.edit_message(
            embed=self.pages[self.current_page], view=self
        )


async def change_xp_scaling_command(
    commandInfo: commandInfo, scaling: str, custom_formula: str = None
):
    if custom_formula:
        custom_formula = custom_formula.replace("x", "level")
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changexpscaling.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changexpscaling.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if scaling == "custom":
        if not checkIfHasPro(commandInfo.guild.id):
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.level.changexpscaling.error.no_pro.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.level.changexpscaling.error.no_pro.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        if not custom_formula:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.level.changexpscaling.error.no_custom_formula.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.level.changexpscaling.error.no_custom_formula.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

    if scaling not in LEVEL_SCALINGS and scaling != "custom":
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changexpscaling.error.invalid_scaling.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changexpscaling.error.invalid_scaling.description",
                available_scalings=", ".join(list(LEVEL_SCALINGS.keys()) + ["custom"]),
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_xp_scaling(str(commandInfo.guild.id), scaling)
    if scaling == "custom":
        await set_custom_formula(str(commandInfo.guild.id), custom_formula)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.changexpscaling.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.changexpscaling.success.description",
            scaling=scaling,
            formula=(
                custom_formula
                if scaling == "custom"
                else tanjunLocalizer.localize(
                    commandInfo.locale,
                    f"commands.level.changexpscaling.formulas.{scaling}",
                )
            ),
        ),
    )

    # Add field to show XP required for first 5 levels
    xp_examples = "\n".join(
        [
            f"Level {i}: {get_xp_for_level(i, scaling, custom_formula)} XP"
            for i in range(1, 6)
        ]
    )
    embed.add_field(
        name=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.changexpscaling.xp_examples"
        ),
        value=xp_examples,
        inline=False,
    )

    await commandInfo.reply(embed=embed)


async def show_xp_scalings(
    commandInfo: commandInfo, start_level: int = 1, end_level: int = 5
):
    if start_level > end_level:
        start_level, end_level = end_level, start_level

    levels_per_page = 15
    total_pages = math.ceil((end_level - start_level + 1) / levels_per_page)
    pages = []

    for page in range(total_pages):
        current_start = start_level + page * levels_per_page
        current_end = min(current_start + levels_per_page - 1, end_level)

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showxpscalings.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.showxpscalings.description",
                start_level=current_start,
                end_level=current_end,
            ),
        )

        for scaling in list(LEVEL_SCALINGS.keys()) + ["custom"]:
            if scaling == "custom":
                if not checkIfHasPro(commandInfo.guild.id):
                    continue
                custom_formula = await get_custom_formula(str(commandInfo.guild.id))
                if not custom_formula:
                    continue
                formula_display = custom_formula
            else:
                formula_display = tanjunLocalizer.localize(
                    commandInfo.locale,
                    f"commands.level.changexpscaling.formulas.{scaling}",
                )

            xp_examples = "\n".join(
                [
                    f"Level {i}: {get_xp_for_level(i, scaling, custom_formula if scaling == 'custom' else None)} XP"
                    for i in range(current_start, current_end + 1)
                ]
            )

            field_content = f"{formula_display}\n{xp_examples}"

            embed.add_field(
                name=tanjunLocalizer.localize(
                    commandInfo.locale,
                    f"commands.level.changexpscaling.scalings.{scaling}",
                ),
                value=field_content,
                inline=False,
            )

        pages.append(embed)

    if not pages:
        await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showxpscalings.no_data"
            )
        )
        return

    if len(pages) == 1:
        await commandInfo.reply(embed=pages[0])
    else:
        view = PaginationView(pages, commandInfo)
        message = await commandInfo.reply(embed=pages[0], view=view)
        view.message = message

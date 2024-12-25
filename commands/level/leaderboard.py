import discord
from api import getLevelLeaderboard, get_xp_scaling, get_custom_formula
import utility
from localizer import tanjunLocalizer


async def leaderboard(commandInfo: utility.commandInfo, page: int = 1):
    if page < 1:
        page = 1
    leaderboard = await getLevelLeaderboard(commandInfo.guild.id)
    scaling = await get_xp_scaling(commandInfo.guild.id)
    custom_formula = await get_custom_formula(commandInfo.guild.id)
    if not leaderboard:
        await commandInfo.message.channel.send(
            tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.leaderboard.no_data"
            )
        )
        return
    if len(leaderboard) == 0:
        await commandInfo.message.channel.send(
            tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.leaderboard.no_data"
            )
        )
        return
    if page > len(leaderboard) / 10 + 1:
        page = int(len(leaderboard) / 10 + 1)

    def generateButtons(page: int, guild: discord.Guild):
        buttons = []
        if page > 1:
            btn = discord.ui.Button(
                label=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.level.leaderboard.previous"
                ),
                style=discord.ButtonStyle.primary,
                custom_id=f"leaderboard_{page - 1}",
            )
            btn.callback = leaderboardButton
            buttons.append(btn)
        if page < int(len(leaderboard) / 10 + 1):
            btn = discord.ui.Button(
                label=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.level.leaderboard.next"
                ),
                style=discord.ButtonStyle.primary,
                custom_id=f"leaderboard_{page + 1}",
            )
            btn.callback = leaderboardButton
            buttons.append(btn)
        return buttons

    async def leaderboardButton(
        button: discord.ui.Button, interaction: discord.Interaction
    ):
        page = int(button.custom_id.split("_")[1])
        scaling = await get_xp_scaling(interaction.guild.id)
        custom_formula = await get_custom_formula(interaction.guild.id)
        embed = generateLeaderboardEmbed(
            page, interaction.guild, scaling, custom_formula
        )
        buttons = generateButtons(page, interaction.guild)
        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)
        await interaction.response.edit_message(embed=embed, view=view)

    def generateLeaderboardEmbed(
        page: int, guild: discord.Guild, scaling: str, custom_formula
    ):
        nonlocal leaderboard
        description = ""
        for i in range(10):
            try:
                placeData = leaderboard[i + (page - 1) * 10]

                user = placeData[0]

                xp = placeData[1]

                level = utility.get_level_for_xp(xp, scaling, custom_formula)

                xp_from_last_level = xp - utility.get_xp_for_level(
                    level - 1, scaling, custom_formula
                )
                xp_till_next_level = utility.get_xp_for_level(
                    level, scaling, custom_formula
                )

                description += f"\n### {i + 1 + (page - 1) * 10}. <@{user}> - {tanjunLocalizer.localize(commandInfo.locale, 'commands.level.leaderboard.data', level=level, xp_from_last_level=xp_from_last_level, xp_till_next_level=xp_till_next_level)}"
            except Exception:
                break
        print(description)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.leaderboard.title", page=page
            ),
            description=description,
        )
        return embed

    embed = generateLeaderboardEmbed(page, commandInfo.guild, scaling, custom_formula)
    buttons = generateButtons(page, commandInfo.guild)
    view = discord.ui.View()
    for button in buttons:
        view.add_item(button)
    await commandInfo.reply(embed=embed, view=view)

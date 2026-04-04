import random
from typing import Any

import discord  # type: ignore[import-not-found]

import utility
from localizer import tanjunLocalizer


async def rps(commandInfo: utility.CommandInfo, user: discord.Member) -> None:  # type: ignore[no-any-unimported]
    player1 = CommandInfo.user  # type: ignore[name-defined]
    player2 = user if user is not None else "tanjun"
    player1_choice = None
    player2_choice = None

    rockLocale = tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.rock")
    paperLocale = tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.paper")
    scissorsLocale = tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.scissors")

    if player2 == "tanjun" or user.bot:
        player2_choice = random.choice([rockLocale, paperLocale, scissorsLocale])

    async def check_winner(interaction: discord.Interaction) -> None:  # type: ignore[no-any-unimported]
        if player1_choice == player2_choice:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.draw"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.rps.drawDescription",
                    player1=player1.mention,
                    player2=player2.mention if player2 != "tanjun" else "tanjun",  # type: ignore[union-attr]
                    player1_choice=player1_choice,
                    player2_choice=player2_choice,
                ),
            )
            await interaction.message.edit(embed=embed, view=None)

        elif (
            (player1_choice == rockLocale and player2_choice == scissorsLocale)  # type: ignore[redundant-expr,unreachable]
            or (player1_choice == paperLocale and player2_choice == rockLocale)  # type: ignore[redundant-expr,unreachable]
            or (player1_choice == scissorsLocale and player2_choice == paperLocale)  # type: ignore[unreachable]
        ):
            embed = utility.tanjunEmbed(  # type: ignore[unreachable]
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.win"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.rps.winDescription",
                    player1=player1.mention,
                    player2=player2.mention if player2 != "tanjun" else "tanjun",
                    player1_choice=player1_choice,
                    player2_choice=player2_choice,
                ),
            )
            await interaction.message.edit(embed=embed, view=None)

        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.lose"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.rps.loseDescription",
                    player1=player1.mention,
                    player2=player2.mention if player2 != "tanjun" else "tanjun",  # type: ignore[union-attr]
                    player1_choice=player1_choice,
                    player2_choice=player2_choice,
                ),
            )
            await interaction.message.edit(embed=embed, view=None)

    class RPSView(discord.ui.View):  # type: ignore[misc,no-any-unimported]
        def __init__(self, commandInfo: utility.CommandInfo, is_player1: bool) -> None:
            super().__init__()
            self.is_player1 = is_player1

        @discord.ui.button(label=rockLocale, style=discord.ButtonStyle.primary, custom_id="rock")  # type: ignore[untyped-decorator]
        async def rock(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            await interaction.response.defer()
            nonlocal player1_choice, player2_choice

            if (
                self.is_player1
                and interaction.user.id != player1.id
                or not self.is_player1
                and interaction.user.id != player2.id  # type: ignore[union-attr]
            ):
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.notYourGame"),
                    ephemeral=True,
                )
                return

            if self.is_player1:
                player1_choice = rockLocale
                if player2 == "tanjun" or user.bot:
                    await check_winner(interaction)
                else:
                    view = RPSView(commandInfo, False)
                    embed = utility.tanjunEmbed(
                        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.title"),
                        description=tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.games.rps.description",
                            player1=player1.mention,
                            player2=player2.mention,  # type: ignore[union-attr]
                        ),
                    )
                    await interaction.message.edit(embed=embed, view=view)

            else:
                player2_choice = rockLocale
                await check_winner(interaction)

        @discord.ui.button(label=paperLocale, style=discord.ButtonStyle.primary, custom_id="paper")  # type: ignore[untyped-decorator]
        async def paper(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            await interaction.response.defer()
            nonlocal player1_choice, player2_choice

            if (
                self.is_player1
                and interaction.user.id != player1.id
                or not self.is_player1
                and interaction.user.id != player2.id  # type: ignore[union-attr]
            ):
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.notYourGame"),
                    ephemeral=True,
                )
                return

            if self.is_player1:
                player1_choice = paperLocale
                if player2 == "tanjun" or user.bot:
                    await check_winner(interaction)
                else:
                    view = RPSView(commandInfo, False)
                    embed = utility.tanjunEmbed(
                        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.title"),
                        description=tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.games.rps.description",
                            player1=player1.mention,
                            player2=player2.mention,  # type: ignore[union-attr]
                        ),
                    )
                    await interaction.message.edit(embed=embed, view=view)

            else:
                player2_choice = paperLocale
                await check_winner(interaction)

        @discord.ui.button(  # type: ignore[untyped-decorator]
            label=scissorsLocale,
            style=discord.ButtonStyle.primary,
            custom_id="scissors",
        )
        async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            await interaction.response.defer()
            nonlocal player1_choice, player2_choice

            if (
                self.is_player1
                and interaction.user.id != player1.id
                or not self.is_player1
                and interaction.user.id != player2.id  # type: ignore[union-attr]
            ):
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.notYourGame"),
                    ephemeral=True,
                )
                return

            if self.is_player1:
                player1_choice = scissorsLocale
                if player2 == "tanjun" or user.bot:
                    await check_winner(interaction)
                else:
                    view = RPSView(commandInfo, False)
                    embed = utility.tanjunEmbed(
                        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.title"),
                        description=tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.games.rps.description",
                            player1=player1.mention,
                            player2=player2.mention,  # type: ignore[union-attr]
                        ),
                    )
                    await interaction.message.edit(embed=embed, view=view)

            else:
                player2_choice = scissorsLocale
                await check_winner(interaction)

    view = RPSView(commandInfo, True)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.rps.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.rps.description",
            player1=player1.mention,
            player2=player2.mention if player2 != "tanjun" else "tanjun",  # type: ignore[union-attr]
        ),
    )
    await commandInfo.reply(embed=embed, view=view)

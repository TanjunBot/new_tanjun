import discord
import random
from localizer import tanjunLocalizer
import utility


async def rps(commandInfo: utility.commandInfo, user: discord.Member):
    player1 = commandInfo.user
    player2 = user if user is not None else "tanjun"
    player1_choice = None
    player2_choice = None

    rockLocale = tanjunLocalizer.localize(commandInfo.locale, "commands.games.rps.rock")
    paperLocale = tanjunLocalizer.localize(
        commandInfo.locale, "commands.games.rps.paper"
    )
    scissorsLocale = tanjunLocalizer.localize(
        commandInfo.locale, "commands.games.rps.scissors"
    )

    if player2 == "tanjun" or user.bot:
        player2_choice = random.choice([rockLocale, paperLocale, scissorsLocale])

    async def check_winner(interaction: discord.Interaction):
        if player1_choice == player2_choice:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.rps.draw"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.rps.drawDescription",
                    player1=player1.mention,
                    player2=player2.mention if player2 != "tanjun" else "tanjun",
                    player1_choice=player1_choice,
                    player2_choice=player2_choice,
                ),
            )
            await interaction.message.edit(embed=embed, view=None)

        elif (
            (player1_choice == rockLocale and player2_choice == scissorsLocale)
            or (player1_choice == paperLocale and player2_choice == rockLocale)
            or (player1_choice == scissorsLocale and player2_choice == paperLocale)
        ):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.rps.win"
                ),
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
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.rps.lose"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.rps.loseDescription",
                    player1=player1.mention,
                    player2=player2.mention if player2 != "tanjun" else "tanjun",
                    player1_choice=player1_choice,
                    player2_choice=player2_choice,
                ),
            )
            await interaction.message.edit(embed=embed, view=None)

    class RPSView(discord.ui.View):
        def __init__(self, commandInfo: utility.commandInfo, is_player1: bool):
            super().__init__()
            self.is_player1 = is_player1

        @discord.ui.button(
            label=rockLocale, style=discord.ButtonStyle.primary, custom_id="rock"
        )
        async def rock(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            nonlocal player1_choice, player2_choice

            if self.is_player1 and interaction.user.id != player1.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.rps.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            elif not self.is_player1 and interaction.user.id != player2.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.rps.notYourGame"
                    ),
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
                        title=tanjunLocalizer.localize(
                            commandInfo.locale, "commands.games.rps.title"
                        ),
                        description=tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.games.rps.description",
                            player1=player1.mention,
                            player2=player2.mention,
                        ),
                    )
                    await interaction.message.edit(embed=embed, view=view)
                    await interaction.response.defer()
            else:
                player2_choice = rockLocale
                await check_winner(interaction)
                await interaction.response.defer()

        @discord.ui.button(
            label=paperLocale, style=discord.ButtonStyle.primary, custom_id="paper"
        )
        async def paper(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            nonlocal player1_choice, player2_choice

            if self.is_player1 and interaction.user.id != player1.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.rps.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            elif not self.is_player1 and interaction.user.id != player2.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.rps.notYourGame"
                    ),
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
                        title=tanjunLocalizer.localize(
                            commandInfo.locale, "commands.games.rps.title"
                        ),
                        description=tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.games.rps.description",
                            player1=player1.mention,
                            player2=player2.mention,
                        ),
                    )
                    await interaction.message.edit(embed=embed, view=view)
                    await interaction.response.defer()
            else:
                player2_choice = paperLocale
                await check_winner(interaction)
                await interaction.response.defer()

        @discord.ui.button(
            label=scissorsLocale,
            style=discord.ButtonStyle.primary,
            custom_id="scissors",
        )
        async def scissors(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            nonlocal player1_choice, player2_choice

            if self.is_player1 and interaction.user.id != player1.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.rps.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            elif not self.is_player1 and interaction.user.id != player2.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.rps.notYourGame"
                    ),
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
                        title=tanjunLocalizer.localize(
                            commandInfo.locale, "commands.games.rps.title"
                        ),
                        description=tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.games.rps.description",
                            player1=player1.mention,
                            player2=player2.mention,
                        ),
                    )
                    await interaction.message.edit(embed=embed, view=view)
                    await interaction.response.defer()
            else:
                player2_choice = scissorsLocale
                await check_winner(interaction)
                await interaction.response.defer()

    view = RPSView(commandInfo, True)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.games.rps.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.rps.description",
            player1=player1.mention,
            player2=player2.mention if player2 != "tanjun" else "tanjun",
        ),
    )
    await commandInfo.reply(embed=embed, view=view)

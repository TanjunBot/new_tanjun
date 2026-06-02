from locale_keys import locale
import random
import discord
import utility

async def rps(command_info: utility.command_info, user: discord.Member):
    player1 = command_info.user
    player2 = user if user is not None else 'tanjun'
    player1_choice = None
    player2_choice = None
    rock_locale = locale.commands.games.rps.rock(command_info.locale)
    paper_locale = locale.commands.games.rps.paper(command_info.locale)
    scissors_locale = locale.commands.games.rps.scissors(command_info.locale)
    if player2 == 'tanjun' or user.bot:
        player2_choice = random.choice([rock_locale, paper_locale, scissors_locale])

    async def check_winner(interaction: discord.Interaction):
        if player1_choice == player2_choice:
            embed = utility.tanjunEmbed(title=locale.commands.games.rps.draw(command_info.locale), description=locale.commands.games.rps.drawDescription(command_info.locale, player1=player1.mention, player2=player2.mention if player2 != 'tanjun' else 'tanjun', player1_choice=player1_choice, player2_choice=player2_choice))
            await interaction.message.edit(embed=embed, view=None)
        elif player1_choice == rock_locale and player2_choice == scissors_locale or (player1_choice == paper_locale and player2_choice == rock_locale) or (player1_choice == scissors_locale and player2_choice == paper_locale):
            embed = utility.tanjunEmbed(title=locale.commands.games.rps.win(command_info.locale), description=locale.commands.games.rps.winDescription(command_info.locale, player1=player1.mention, player2=player2.mention if player2 != 'tanjun' else 'tanjun', player1_choice=player1_choice, player2_choice=player2_choice))
            await interaction.message.edit(embed=embed, view=None)
        else:
            embed = utility.tanjunEmbed(title=locale.commands.games.rps.lose(command_info.locale), description=locale.commands.games.rps.loseDescription(command_info.locale, player1=player1.mention, player2=player2.mention if player2 != 'tanjun' else 'tanjun', player1_choice=player1_choice, player2_choice=player2_choice))
            await interaction.message.edit(embed=embed, view=None)

    class RPSView(discord.ui.View):

        def __init__(self, command_info: utility.command_info, is_player1: bool):
            super().__init__()
            self.is_player1 = is_player1

        @discord.ui.button(label=rock_locale, style=discord.ButtonStyle.primary, custom_id='rock')
        async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            nonlocal player1_choice, player2_choice
            if self.is_player1 and interaction.user.id != player1.id or (not self.is_player1 and interaction.user.id != player2.id):
                await interaction.followup.send(locale.commands.games.rps.notYourGame(command_info.locale), ephemeral=True)
                return
            if self.is_player1:
                player1_choice = rock_locale
                if player2 == 'tanjun' or user.bot:
                    await check_winner(interaction)
                else:
                    view = RPSView(command_info, False)
                    embed = utility.tanjunEmbed(title=locale.commands.games.rps.title(command_info.locale), description=locale.commands.games.rps.description(command_info.locale, player1=player1.mention, player2=player2.mention))
                    await interaction.message.edit(embed=embed, view=view)
            else:
                player2_choice = rock_locale
                await check_winner(interaction)

        @discord.ui.button(label=paper_locale, style=discord.ButtonStyle.primary, custom_id='paper')
        async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            nonlocal player1_choice, player2_choice
            if self.is_player1 and interaction.user.id != player1.id or (not self.is_player1 and interaction.user.id != player2.id):
                await interaction.followup.send(locale.commands.games.rps.notYourGame(command_info.locale), ephemeral=True)
                return
            if self.is_player1:
                player1_choice = paper_locale
                if player2 == 'tanjun' or user.bot:
                    await check_winner(interaction)
                else:
                    view = RPSView(command_info, False)
                    embed = utility.tanjunEmbed(title=locale.commands.games.rps.title(command_info.locale), description=locale.commands.games.rps.description(command_info.locale, player1=player1.mention, player2=player2.mention))
                    await interaction.message.edit(embed=embed, view=view)
            else:
                player2_choice = paper_locale
                await check_winner(interaction)

        @discord.ui.button(label=scissors_locale, style=discord.ButtonStyle.primary, custom_id='scissors')
        async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            nonlocal player1_choice, player2_choice
            if self.is_player1 and interaction.user.id != player1.id or (not self.is_player1 and interaction.user.id != player2.id):
                await interaction.followup.send(locale.commands.games.rps.notYourGame(command_info.locale), ephemeral=True)
                return
            if self.is_player1:
                player1_choice = scissors_locale
                if player2 == 'tanjun' or user.bot:
                    await check_winner(interaction)
                else:
                    view = RPSView(command_info, False)
                    embed = utility.tanjunEmbed(title=locale.commands.games.rps.title(command_info.locale), description=locale.commands.games.rps.description(command_info.locale, player1=player1.mention, player2=player2.mention))
                    await interaction.message.edit(embed=embed, view=view)
            else:
                player2_choice = scissors_locale
                await check_winner(interaction)
    view = RPSView(command_info, True)
    embed = utility.tanjunEmbed(title=locale.commands.games.rps.title(command_info.locale), description=locale.commands.games.rps.description(command_info.locale, player1=player1.mention, player2=player2.mention if player2 != 'tanjun' else 'tanjun'))
    await command_info.reply(embed=embed, view=view)
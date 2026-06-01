from __future__ import annotations
from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.games.advanced_tic_tac_toe import advanced_tic_tac_toe
from commands.games.akinator import akinator
from commands.games.battleship import battleship
from commands.games.connect4 import connect4
from commands.games.flag_quiz import flag_quiz
from commands.games.hangman import hangman
from commands.games.memory import memory
from commands.games.rps import rps
from commands.games.tic_tac_toe import tic_tac_toe
from commands.games.wordle import wordle

class GameCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.games.ttt.name.discord_key, description=locale.games.ttt.description.discord_key)
    @app_commands.describe(user=locale.games.ttt.params.user.description.discord_key)
    async def tic_tac_toe_cmd(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await tic_tac_toe(command_info, interaction.user, user)

    @app_commands.command(name=locale.games.connect4.name.discord_key, description=locale.games.connect4.description.discord_key)
    @app_commands.describe(size=locale.games.connect4.params.size.description.discord_key)
    @app_commands.choices(size=[app_commands.Choice(value='7,6', name=locale.games.connect4.params.size.default.discord_key), app_commands.Choice(value='8,7', name=locale.games.connect4.params.size._8x7.discord_key), app_commands.Choice(value='9,8', name=locale.games.connect4.params.size._9x8.discord_key), app_commands.Choice(value='10,9', name=locale.games.connect4.params.size._10x9.discord_key), app_commands.Choice(value='11,10', name=locale.games.connect4.params.size._11x10.discord_key), app_commands.Choice(value='12,11', name=locale.games.connect4.params.size._12x11.discord_key), app_commands.Choice(value='12,12', name=locale.games.connect4.params.size._12x12.discord_key), app_commands.Choice(value='4,4', name=locale.games.connect4.params.size._4x4.discord_key)])
    async def connect4_cmd(self, interaction: discord.Interaction, user: discord.Member=None, size: app_commands.Choice[str]='7,6') -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        size = size.value.split(',') if size != '7,6' else ['7', '6']
        await connect4(command_info, interaction.user, user, int(size[0]), int(size[1]))

    @app_commands.command(name=locale.games.akinator.name.discord_key, description=locale.games.akinator.description.discord_key)
    @app_commands.describe(theme=locale.games.akinator.params.theme.description.discord_key)
    @app_commands.choices(theme=[app_commands.Choice(value='characters', name=locale.games.akinator.params.theme.characters.discord_key), app_commands.Choice(value='animals', name=locale.games.akinator.params.theme.animals.discord_key), app_commands.Choice(value='objects', name=locale.games.akinator.params.theme.objects.discord_key)])
    async def akinator_cmd(self, interaction: discord.Interaction, theme: app_commands.Choice[str]='characters') -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await akinator(command_info, theme.value if theme != 'characters' else 'characters')

    @app_commands.command(name=locale.games.wordle.name.discord_key, description=locale.games.wordle.description.discord_key)
    @app_commands.describe(language=locale.games.wordle.params.language.description.discord_key)
    @app_commands.choices(language=[app_commands.Choice(value='bg', name=locale.games.wordle.params.language.bg.discord_key), app_commands.Choice(value='cs', name=locale.games.wordle.params.language.cs.discord_key), app_commands.Choice(value='da', name=locale.games.wordle.params.language.da.discord_key), app_commands.Choice(value='de', name=locale.games.wordle.params.language.de.discord_key), app_commands.Choice(value='el', name=locale.games.wordle.params.language.el.discord_key), app_commands.Choice(value='en', name=locale.games.wordle.params.language.en.discord_key), app_commands.Choice(value='es', name=locale.games.wordle.params.language.es.discord_key), app_commands.Choice(value='fi', name=locale.games.wordle.params.language.fi.discord_key), app_commands.Choice(value='fr', name=locale.games.wordle.params.language.fr.discord_key), app_commands.Choice(value='hi', name=locale.games.wordle.params.language.hi.discord_key), app_commands.Choice(value='hu', name=locale.games.wordle.params.language.hu.discord_key), app_commands.Choice(value='id', name=locale.games.wordle.params.language.id.discord_key), app_commands.Choice(value='it', name=locale.games.wordle.params.language.it.discord_key), app_commands.Choice(value='ja', name=locale.games.wordle.params.language.ja.discord_key), app_commands.Choice(value='ko', name=locale.games.wordle.params.language.ko.discord_key), app_commands.Choice(value='lt', name=locale.games.wordle.params.language.lt.discord_key), app_commands.Choice(value='nb', name=locale.games.wordle.params.language.nb.discord_key), app_commands.Choice(value='nl', name=locale.games.wordle.params.language.nl.discord_key), app_commands.Choice(value='pl', name=locale.games.wordle.params.language.pl.discord_key), app_commands.Choice(value='pt', name=locale.games.wordle.params.language.pt.discord_key), app_commands.Choice(value='ru', name=locale.games.wordle.params.language.ru.discord_key), app_commands.Choice(value='zh', name=locale.games.wordle.params.language.zh.discord_key)])
    @app_commands.describe(language=locale.games.wordle.params.language.description.discord_key)
    async def wordle_cmd(self, interaction: discord.Interaction, language: app_commands.Choice[str]='own') -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await wordle(command_info, language.value if language != 'own' else 'own')

    @app_commands.command(name=locale.games.hangman.name.discord_key, description=locale.games.hangman.description.discord_key)
    @app_commands.describe(language=locale.games.hangman.params.language.description.discord_key)
    @app_commands.choices(language=[app_commands.Choice(value='bg', name=locale.games.hangman.params.language.bg.discord_key), app_commands.Choice(value='cs', name=locale.games.hangman.params.language.cs.discord_key), app_commands.Choice(value='da', name=locale.games.hangman.params.language.da.discord_key), app_commands.Choice(value='de', name=locale.games.hangman.params.language.de.discord_key), app_commands.Choice(value='el', name=locale.games.hangman.params.language.el.discord_key), app_commands.Choice(value='en', name=locale.games.hangman.params.language.en.discord_key), app_commands.Choice(value='es', name=locale.games.hangman.params.language.es.discord_key), app_commands.Choice(value='fi', name=locale.games.hangman.params.language.fi.discord_key), app_commands.Choice(value='fr', name=locale.games.hangman.params.language.fr.discord_key), app_commands.Choice(value='hi', name=locale.games.hangman.params.language.hi.discord_key), app_commands.Choice(value='hu', name=locale.games.hangman.params.language.hu.discord_key), app_commands.Choice(value='id', name=locale.games.hangman.params.language.id.discord_key), app_commands.Choice(value='it', name=locale.games.hangman.params.language.it.discord_key), app_commands.Choice(value='ja', name=locale.games.hangman.params.language.ja.discord_key), app_commands.Choice(value='ko', name=locale.games.hangman.params.language.ko.discord_key), app_commands.Choice(value='lt', name=locale.games.hangman.params.language.lt.discord_key), app_commands.Choice(value='nb', name=locale.games.hangman.params.language.nb.discord_key), app_commands.Choice(value='nl', name=locale.games.hangman.params.language.nl.discord_key), app_commands.Choice(value='pl', name=locale.games.hangman.params.language.pl.discord_key), app_commands.Choice(value='pt', name=locale.games.hangman.params.language.pt.discord_key), app_commands.Choice(value='ru', name=locale.games.hangman.params.language.ru.discord_key), app_commands.Choice(value='zh', name=locale.games.hangman.params.language.zh.discord_key)])
    async def hangman_cmd(self, interaction: discord.Interaction, language: app_commands.Choice[str]='own') -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await hangman(command_info, language.value if language != 'own' else 'own')

    @app_commands.command(name=locale.games.flagquiz.name.discord_key, description=locale.games.flagquiz.description.discord_key)
    async def flag_quiz_cmd(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await flag_quiz(command_info)

    @app_commands.command(name=locale.games.rps.name.discord_key, description=locale.games.rps.description.discord_key)
    @app_commands.describe(user=locale.games.rps.params.user.description.discord_key)
    async def rps_cmd(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await rps(command_info, user)

    @app_commands.command(name=locale.games.battleship.name.discord_key, description=locale.games.battleship.description.discord_key)
    @app_commands.describe(user=locale.games.battleship.params.user.description.discord_key)
    async def battleship_cmd(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await battleship(command_info, interaction.user, user)

    @app_commands.command(name=locale.games.memory.name.discord_key, description=locale.games.memory.description.discord_key)
    async def memory_cmd(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await memory(command_info, interaction.user)

    @app_commands.command(name=locale.games.advanced.ttt.name.discord_key, description=locale.games.advanced.ttt.description.discord_key)
    @app_commands.describe(user=locale.games.advanced.ttt.params.user.description.discord_key)
    async def advanced_ttt_cmd(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await advanced_tic_tac_toe(command_info, interaction.user, user)

class GameCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        game_cmds = GameCommands(name=locale.games.name.discord_key, description=locale.games.description.discord_key)
        if self.bot.tree:
            self.bot.tree.add_command(game_cmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GameCog(bot))
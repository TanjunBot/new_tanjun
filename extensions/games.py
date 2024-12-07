import discord
from discord.ext import commands
from discord import app_commands
import utility

from commands.games.tic_tac_toe import tic_tac_toe
from commands.games.connect4 import connect4
from commands.games.akinator import akinator
from commands.games.wordle import wordle
from commands.games.hangman import hangman
from commands.games.flag_quiz import flag_quiz
from commands.games.rps import rps

class gameCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("ttt_name"),
        description=app_commands.locale_str("ttt_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("ttt_user_description"),
    )
    async def tic_tac_toe_cmd(self, ctx, user: discord.Member = None):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await tic_tac_toe(commandInfo, ctx.user, user)

    @app_commands.command(
        name=app_commands.locale_str("connect4_name"),
        description=app_commands.locale_str("connect4_description"),
    )
    @app_commands.choices(
        size=[
            app_commands.Choice(
                value="7,6",
                name=app_commands.locale_str("admin_purge_params_setting_default"),
            ),
            app_commands.Choice(
                value="8,7",
                name=app_commands.locale_str("admin_purge_params_setting_8x7"),
            ),
            app_commands.Choice(
                value="9,8",
                name=app_commands.locale_str("admin_purge_params_setting_9x8"),
            ),
            app_commands.Choice(
                value="10,9",
                name=app_commands.locale_str("admin_purge_params_setting_10x9"),
            ),
            app_commands.Choice(
                value="11,10",
                name=app_commands.locale_str(
                    "admin_purge_params_setting_11x10"
                ),
            ),
            app_commands.Choice(
                value="12,11",
                name=app_commands.locale_str("admin_purge_params_setting_12x11"),
            ),
            app_commands.Choice(
                value="12,12",
                name=app_commands.locale_str("admin_purge_params_setting_12x12"),
            ),
            app_commands.Choice(
                value="4,4",
                name=app_commands.locale_str("admin_purge_params_setting_4x4"),
            ),
        ]
    )
    async def connect4_cmd(self, ctx, user: discord.Member = None, size: app_commands.Choice[str] = "7,6"):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        size = size.value.split(",") if size != "7,6" else "7,6".split(",")
        await connect4(commandInfo, ctx.user, user, int(size[0]), int(size[1]))

    @app_commands.command(
        name=app_commands.locale_str("akinator_name"),
        description=app_commands.locale_str("akinator_description"),
    )
    @app_commands.choices(
        theme=[
            app_commands.Choice(
                value="characters",
                name=app_commands.locale_str("akinator_theme_characters"),
            ),
            app_commands.Choice(
                value="animals",
                name=app_commands.locale_str("akinator_theme_animals"),
            ),
            app_commands.Choice(
                value="objects",
                name=app_commands.locale_str("akinator_theme_objects"),
            ),
        ]
    )
    async def akinator_cmd(self, ctx, theme: app_commands.Choice[str] = "characters"):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await akinator(commandInfo, theme.value if theme != "characters" else "characters")

    @app_commands.command(
        name=app_commands.locale_str("wordle_name"),
        description=app_commands.locale_str("wordle_description"),
    )
    @app_commands.choices(
        language=[
            app_commands.Choice(
                value="bg",
                name=app_commands.locale_str("wordle_language_bg"),
            ),
            app_commands.Choice(
                value="cs",
                name=app_commands.locale_str("wordle_language_cs"),
            ),
            app_commands.Choice(
                value="da",
                name=app_commands.locale_str("wordle_language_da"),
            ),
            app_commands.Choice(
                value="de",
                name=app_commands.locale_str("wordle_language_de"),
            ),
            app_commands.Choice(
                value="el",
                name=app_commands.locale_str("wordle_language_el"),
            ),
            app_commands.Choice(
                value="en",
                name=app_commands.locale_str("wordle_language_en"),
            ),
            app_commands.Choice(
                value="es",
                name=app_commands.locale_str("wordle_language_es"),
            ),
            app_commands.Choice(
                value="fi",
                name=app_commands.locale_str("wordle_language_fi"),
            ),
            app_commands.Choice(
                value="fr",
                name=app_commands.locale_str("wordle_language_fr"),
            ),
            app_commands.Choice(
                value="hi",
                name=app_commands.locale_str("wordle_language_hi"),
            ),
            app_commands.Choice(
                value="hu",
                name=app_commands.locale_str("wordle_language_hu"),
            ),
            app_commands.Choice(
                value="id",
                name=app_commands.locale_str("wordle_language_id"),
            ),
            app_commands.Choice(
                value="it",
                name=app_commands.locale_str("wordle_language_it"),
            ),
            app_commands.Choice(
                value="ja",
                name=app_commands.locale_str("wordle_language_ja"),
            ),
            app_commands.Choice(
                value="ko",
                name=app_commands.locale_str("wordle_language_ko"),
            ),
            app_commands.Choice(
                value="lt",
                name=app_commands.locale_str("wordle_language_lt"),
            ),
            app_commands.Choice(
                value="nb",
                name=app_commands.locale_str("wordle_language_nb"),
            ),
            app_commands.Choice(
                value="nl",
                name=app_commands.locale_str("wordle_language_nl"),
            ),
            app_commands.Choice(
                value="pl",
                name=app_commands.locale_str("wordle_language_pl"),
            ),
            app_commands.Choice(
                value="pt",
                name=app_commands.locale_str("wordle_language_pt"),
            ),
            app_commands.Choice(
                value="ru",
                name=app_commands.locale_str("wordle_language_ru"),
            ),
            app_commands.Choice(
                value="zh",
                name=app_commands.locale_str("wordle_language_zh"),
            ),
        ]
    )
    @app_commands.describe(
        language=app_commands.locale_str("wordle_language_description"),
    )
    async def wordle_cmd(self, ctx, language: app_commands.Choice[str] = "own"):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await wordle(commandInfo, language.value if language != "own" else "own")

    @app_commands.command(
    name=app_commands.locale_str("hangman_name"),
    description=app_commands.locale_str("hangman_description"),
    )
    @app_commands.choices(
        language=[
            app_commands.Choice(
                value="bg",
                name=app_commands.locale_str("wordle_language_bg"),
            ),
            app_commands.Choice(
                value="cs",
                name=app_commands.locale_str("wordle_language_cs"),
            ),
            app_commands.Choice(
                value="da",
                name=app_commands.locale_str("wordle_language_da"),
            ),
            app_commands.Choice(
                value="de",
                name=app_commands.locale_str("wordle_language_de"),
            ),
            app_commands.Choice(
                value="el",
                name=app_commands.locale_str("wordle_language_el"),
            ),
            app_commands.Choice(
                value="en",
                name=app_commands.locale_str("wordle_language_en"),
            ),
            app_commands.Choice(
                value="es",
                name=app_commands.locale_str("wordle_language_es"),
            ),
            app_commands.Choice(
                value="fi",
                name=app_commands.locale_str("wordle_language_fi"),
            ),
            app_commands.Choice(
                value="fr",
                name=app_commands.locale_str("wordle_language_fr"),
            ),
            app_commands.Choice(
                value="hi",
                name=app_commands.locale_str("wordle_language_hi"),
            ),
            app_commands.Choice(
                value="hu",
                name=app_commands.locale_str("wordle_language_hu"),
            ),
            app_commands.Choice(
                value="id",
                name=app_commands.locale_str("wordle_language_id"),
            ),
            app_commands.Choice(
                value="it",
                name=app_commands.locale_str("wordle_language_it"),
            ),
            app_commands.Choice(
                value="ja",
                name=app_commands.locale_str("wordle_language_ja"),
            ),
            app_commands.Choice(
                value="ko",
                name=app_commands.locale_str("wordle_language_ko"),
            ),
            app_commands.Choice(
                value="lt",
                name=app_commands.locale_str("wordle_language_lt"),
            ),
            app_commands.Choice(
                value="nb",
                name=app_commands.locale_str("wordle_language_nb"),
            ),
            app_commands.Choice(
                value="nl",
                name=app_commands.locale_str("wordle_language_nl"),
            ),
            app_commands.Choice(
                value="pl",
                name=app_commands.locale_str("wordle_language_pl"),
            ),
            app_commands.Choice(
                value="pt",
                name=app_commands.locale_str("wordle_language_pt"),
            ),
            app_commands.Choice(
                value="ru",
                name=app_commands.locale_str("wordle_language_ru"),
            ),
            app_commands.Choice(
                value="zh",
                name=app_commands.locale_str("wordle_language_zh"),
            ),
        ]
    )
    @app_commands.describe(
        language=app_commands.locale_str("hangman_language_description"),
    )
    async def hangman_cmd(self, ctx, language: app_commands.Choice[str] = "own"):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await hangman(commandInfo, language.value if language != "own" else "own")

    @app_commands.command(
        name=app_commands.locale_str("flag_quiz_name"),
        description=app_commands.locale_str("flag_quiz_description"),
    )
    async def flag_quiz_cmd(self, ctx):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await flag_quiz(commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("rps_name"),
        description=app_commands.locale_str("rps_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("rps_user_description"),
    )
    async def rps_cmd(self, ctx, user: discord.Member = None):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await rps(commandInfo, user)

class gameCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        gameCmds = gameCommands(name="gamecommands", description="Game Commands")
        self.bot.tree.add_command(gameCmds)


async def setup(bot):
    await bot.add_cog(gameCog(bot))

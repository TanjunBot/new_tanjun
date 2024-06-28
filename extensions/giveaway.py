import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.giveaway.start import start_giveaway


class GiveawayCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("giveaway_start_name"),
        description=app_commands.locale_str("giveaway_start_description"),
    )
    @app_commands.describe(
        title=app_commands.locale_str("giveaway_start_params_title_description"),
        winners=app_commands.locale_str("giveaway_start_params_winners_description"),
        with_button=app_commands.locale_str(
            "giveaway_start_params_with_button_description"
        ),
        custom_name=app_commands.locale_str(
            "giveaway_start_params_custom_name_description"
        ),
        sponsor=app_commands.locale_str("giveaway_start_params_sponsor_description"),
        price=app_commands.locale_str("giveaway_start_params_price_description"),
        message=app_commands.locale_str("giveaway_start_params_message_description"),
        end_time=app_commands.locale_str("giveaway_start_params_end_time_description"),
        start_time=app_commands.locale_str(
            "giveaway_start_params_start_time_description"
        ),
        new_message_requirement=app_commands.locale_str(
            "giveaway_start_params_new_message_requirement_description"
        ),
        day_requirement=app_commands.locale_str(
            "giveaway_start_params_day_requirement_description"
        ),
        role_requirement=app_commands.locale_str(
            "giveaway_start_params_role_requirement_description"
        ),
        voice_requirement=app_commands.locale_str(
            "giveaway_start_params_voice_requirement_description"
        ),
    )
    async def start(
        self,
        ctx: discord.Interaction,
        title: str,
        winners: int = 1,
        with_button: bool = True,
        custom_name: str = None,
        sponsor: discord.Member = None,
        price: str = None,
        message: str = None,
        end_time: str = None,
        start_time: str = None,
        new_message_requirement: int = 0,
        day_requirement: int = 0,
        role_requirement: discord.Role = None,
        voice_requirement: int = 0,
    ):
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
        await ctx.response.defer()
        await start_giveaway(
            commandInfo,
            title,
            winners,
            with_button,
            custom_name,
            sponsor,
            price,
            message,
            end_time,
            start_time,
            new_message_requirement,
            day_requirement,
            role_requirement,
            voice_requirement,
        )


class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        giveaway_commands = GiveawayCommands(
            name="giveaway", description="Giveaway Commands"
        )
        self.bot.tree.add_command(giveaway_commands)


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))

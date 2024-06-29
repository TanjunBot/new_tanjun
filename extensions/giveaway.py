import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.giveaway.start import start_giveaway
from commands.giveaway.add_blacklist_role import add_blacklist_role

class BlacklistCommands(discord.app_commands.Group):
    @commands.command(
        name=app_commands.locale_str("giveaway_blacklist_add_role_name"),
        description=app_commands.locale_str("giveaway_blacklist_add_role_description"),
    )
    @commands.describe(
        role=app_commands.locale_str("giveaway_blacklist_add_role_role_description"),
    )
    async def add_role(
        self,
        ctx: discord.Interaction,
        role: discord.Role,
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
        await add_blacklist_role(
            commandInfo=commandInfo,
            role=role,
        )

class GiveawayCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("giveaway_start_name"),
        description=app_commands.locale_str("giveaway_start_description"),
    )
    @app_commands.describe(
        title=app_commands.locale_str("giveaway_start_params_title_description"),
        channel=app_commands.locale_str("giveaway_start_params_channel_description"),
    )
    async def start(
        self,
        ctx: discord.Interaction,
        title: str,
        channel: discord.TextChannel = None,
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

        if not channel:
            channel = ctx.channel

        await ctx.response.defer()
        await start_giveaway(
            commandInfo=commandInfo,
            title=title,
            target_channel=channel,
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

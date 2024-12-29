# Unused imports:
# from localizer import tanjunLocalizer
# from typing import List, Optional
import discord
from discord.ext import commands
from discord import app_commands
import utility

from commands.fun.funcommands import fun_command


class funCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("fun_hug_name"),
        description=app_commands.locale_str("fun_hug_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_hug_params_member_description"),
        message=app_commands.locale_str("fun_hug_params_message_description"),
    )
    async def hug(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'hug'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_kiss_name"),
        description=app_commands.locale_str("fun_kiss_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_kiss_params_member_description"),
        message=app_commands.locale_str("fun_kiss_params_message_description"),
    )
    async def kiss(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'kiss'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_boop_name"),
        description=app_commands.locale_str("fun_boop_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_boop_params_member_description"),
        message=app_commands.locale_str("fun_boop_params_message_description"),
    )
    async def boop(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'boop'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_wave_name"),
        description=app_commands.locale_str("fun_wave_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_wave_params_member_description"),
        message=app_commands.locale_str("fun_wave_params_message_description"),
    )
    async def wave(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'wave'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_slap_name"),
        description=app_commands.locale_str("fun_slap_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_slap_params_member_description"),
        message=app_commands.locale_str("fun_slap_params_message_description"),
    )
    async def slap(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'slap'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_laugh_name"),
        description=app_commands.locale_str("fun_laugh_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_laugh_params_member_description"),
        message=app_commands.locale_str("fun_laugh_params_message_description"),
    )
    async def laugh(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'laugh'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_tickle_name"),
        description=app_commands.locale_str("fun_tickle_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_tickle_params_member_description"),
        message=app_commands.locale_str("fun_tickle_params_message_description"),
    )
    async def tickle(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'tickle'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_pat_name"),
        description=app_commands.locale_str("fun_pat_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_pat_params_member_description"),
        message=app_commands.locale_str("fun_pat_params_message_description"),
    )
    async def pat(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'pat'
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_poke_name"),
        description=app_commands.locale_str("fun_poke_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_poke_params_member_description"),
        message=app_commands.locale_str("fun_poke_params_message_description"),
    )
    async def poke(self, ctx, user: discord.Member, message: app_commands.Range[str, 0, 2000] = None):
        fun_type = 'poke'
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

        await fun_command(commandInfo, fun_type, user, message)


class funCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        utilityCmds = funCommands(name=app_commands.locale_str("funcmd_name"), description=app_commands.locale_str("funcmd_description"))
        self.bot.tree.add_command(utilityCmds)


async def setup(bot):
    await bot.add_cog(funCog(bot))

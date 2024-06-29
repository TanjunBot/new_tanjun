import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.giveaway.start import start_giveaway
from commands.giveaway.add_blacklist_role import add_blacklist_role
from commands.giveaway.remove_blacklist_role import remove_blacklist_role
from commands.giveaway.add_blacklist_user import add_blacklist_user
from commands.giveaway.remove_blacklist_user import remove_blacklist_user
from commands.giveaway.list_blacklist import list_blacklist
from commands.giveaway.end_giveaway import end_giveaway 
from commands.giveaway.reroll_giveaway import reroll_giveaway
from commands.giveaway.edit_giveaway import edit_giveaway

class BlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_add_role_name"),
        description=app_commands.locale_str("giveaway_bl_add_role_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("giveaway_bl_add_role_role_description"),
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

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_remove_role_name"),
        description=app_commands.locale_str("giveaway_bl_remove_role_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("giveaway_bl_remove_role_role_description"),
    )
    async def remove_role(
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
        await remove_blacklist_role(
            commandInfo=commandInfo,
            role=role,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_add_user_name"),
        description=app_commands.locale_str("giveaway_bl_add_user_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("giveaway_bl_add_user_user_description"),
    )
    async def add_user(
        self,
        ctx: discord.Interaction,
        user: discord.User,
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
        await add_blacklist_user(
            commandInfo=commandInfo,
            user=user,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_remove_user_name"),
        description=app_commands.locale_str("giveaway_bl_remove_user_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("giveaway_bl_remove_user_user_description"),
    )
    async def remove_user(
        self,
        ctx: discord.Interaction,
        user: discord.User,
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
        await remove_blacklist_user(
            commandInfo=commandInfo,
            user=user,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_list_name"),
        description=app_commands.locale_str("giveaway_bl_list_description"),
    )
    async def list(
        self,
        ctx: discord.Interaction,
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
        await list_blacklist(
            commandInfo=commandInfo,
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

    @app_commands.command(
        name=app_commands.locale_str("giveaway_end_name"),
        description=app_commands.locale_str("giveaway_end_description"),
    )
    @app_commands.describe(
        giveawayid=app_commands.locale_str("giveaway_end_params_giveawayid_description"),
    )
    async def end(
        self,
        ctx: discord.Interaction,
        giveawayid: int,
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
        await end_giveaway(
            commandInfo=commandInfo,
            giveawayId=giveawayid,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_reroll_name"),
        description=app_commands.locale_str("giveaway_reroll_description"),
    )
    @app_commands.describe(
        giveawayid=app_commands.locale_str("giveaway_reroll_params_giveawayid_description"),
    )
    async def reroll(
        self,
        ctx: discord.Interaction,
        giveawayid: int,
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
        await reroll_giveaway(
            commandInfo=commandInfo,
            giveawayId=giveawayid,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_edit_name"),
        description=app_commands.locale_str("giveaway_edit_description"),
    )
    @app_commands.describe(
        giveawayid=app_commands.locale_str("giveaway_edit_params_giveawayid_description"),
    )
    async def edit(
        self,
        ctx: discord.Interaction,
        giveawayid: int,
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
        await edit_giveaway(
            commandInfo=commandInfo,
            giveawayId=giveawayid,
        )



class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        giveaway_commands = GiveawayCommands(
            name="giveaway", description="Giveaway Commands"
        )
        blacklistCmds = BlacklistCommands(
            name="blacklist", description="Blacklist Commands"
        )
        giveaway_commands.add_command(blacklistCmds)
        self.bot.tree.add_command(giveaway_commands)


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))

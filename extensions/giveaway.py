from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.giveaway.add_blacklist_role import add_blacklist_role
from commands.giveaway.add_blacklist_user import add_blacklist_user
from commands.giveaway.edit_giveaway import edit_giveaway
from commands.giveaway.end_giveaway import end_giveaway
from commands.giveaway.list_blacklist import list_blacklist
from commands.giveaway.remove_blacklist_role import remove_blacklist_role
from commands.giveaway.remove_blacklist_user import remove_blacklist_user
from commands.giveaway.reroll_giveaway import reroll_giveaway
from commands.giveaway.start import start_giveaway

class BlacklistCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.giveaway.bl.add.role.name.discord_key, description=locale.giveaway.bl.add.role.description.discord_key)
    @app_commands.describe(role=locale.giveaway.bl.add.role.role.description.discord_key)
    async def add_role(self, ctx: discord.Interaction, role: discord.Role) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await add_blacklist_role(command_info=command_info, role=role)

    @app_commands.command(name=locale.giveaway.bl.remove.role.name.discord_key, description=locale.giveaway.bl.remove.role.description.discord_key)
    @app_commands.describe(role=locale.giveaway.bl.remove.role.role.description.discord_key)
    async def remove_role(self, ctx: discord.Interaction, role: discord.Role) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await remove_blacklist_role(command_info=command_info, role=role)

    @app_commands.command(name=locale.giveaway.bl.add.user.name.discord_key, description=locale.giveaway.bl.add.user.description.discord_key)
    @app_commands.describe(user=locale.giveaway.bl.add.user.user.description.discord_key)
    async def add_user(self, ctx: discord.Interaction, user: discord.User) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await add_blacklist_user(command_info=command_info, user=user)

    @app_commands.command(name=locale.giveaway.bl.remove.user.name.discord_key, description=locale.giveaway.bl.remove.user.description.discord_key)
    @app_commands.describe(user=locale.giveaway.bl.remove.user.user.description.discord_key)
    async def remove_user(self, ctx: discord.Interaction, user: discord.User) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await remove_blacklist_user(command_info=command_info, user=user)

    @app_commands.command(name=locale.giveaway.bl.list.name.discord_key, description=locale.giveaway.bl.list.description.discord_key)
    async def list(self, ctx: discord.Interaction) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await list_blacklist(command_info=command_info)

class GiveawayCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.giveaway.start.name.discord_key, description=locale.giveaway.start.description.discord_key)
    @app_commands.describe(title=locale.giveaway.start.params.title.description.discord_key, channel=locale.giveaway.start.params.channel.description.discord_key)
    async def start(self, ctx: discord.Interaction, title: app_commands.Range[str, 0, 128], channel: discord.TextChannel=None) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if not channel:
            channel = ctx.channel
        await ctx.response.defer()
        await start_giveaway(command_info=command_info, title=title, target_channel=channel)

    @app_commands.command(name=locale.giveaway.end.name.discord_key, description=locale.giveaway.end.description.discord_key)
    @app_commands.describe(giveawayid=locale.giveaway.end.params.giveawayid.description.discord_key)
    async def end(self, ctx: discord.Interaction, giveawayid: app_commands.Range[int, 1, 4294967295]) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await end_giveaway(command_info=command_info, giveaway_id=giveawayid)

    @app_commands.command(name=locale.giveaway.reroll.name.discord_key, description=locale.giveaway.reroll.description.discord_key)
    @app_commands.describe(giveawayid=locale.giveaway.reroll.params.giveawayid.description.discord_key)
    async def reroll(self, ctx: discord.Interaction, giveawayid: app_commands.Range[int, 1, 4294967295]) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await reroll_giveaway(command_info=command_info, giveaway_id=giveawayid)

    @app_commands.command(name=locale.giveaway.edit.name.discord_key, description=locale.giveaway.edit.description.discord_key)
    @app_commands.describe(giveawayid=locale.giveaway.edit.params.giveawayid.description.discord_key)
    async def edit(self, ctx: discord.Interaction, giveawayid: app_commands.Range[int, 1, 4294967295]) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=cast(discord.abc.GuildChannel, ctx.channel), guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await ctx.response.defer()
        await edit_giveaway(command_info=command_info, giveaway_id=giveawayid)

class GiveawayCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        giveaway_commands = GiveawayCommands(name=locale.giveaway.name.discord_key, description=locale.giveaway.description.discord_key)
        blacklist_cmds = BlacklistCommands(name=locale.giveaway.blacklist.name.discord_key, description=locale.giveaway.blacklist.description.discord_key)
        giveaway_commands.add_command(blacklist_cmds)
        if self.bot.tree:
            self.bot.tree.add_command(giveaway_commands)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GiveawayCog(bot))
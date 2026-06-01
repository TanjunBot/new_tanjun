from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.fun.funcommands import fun_command

class FunCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.fun.hug.name.discord_key, description=locale.fun.hug.description.discord_key)
    @app_commands.describe(user=locale.fun.hug.params.member.description.discord_key, message=locale.fun.hug.params.message.description.discord_key)
    async def hug(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'hug', user, message)

    @app_commands.command(name=locale.fun.kiss.name.discord_key, description=locale.fun.kiss.description.discord_key)
    @app_commands.describe(user=locale.fun.kiss.params.member.description.discord_key, message=locale.fun.kiss.params.message.description.discord_key)
    async def kiss(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'kiss', user, message)

    @app_commands.command(name=locale.fun.boop.name.discord_key, description=locale.fun.boop.description.discord_key)
    @app_commands.describe(user=locale.fun.boop.params.member.description.discord_key, message=locale.fun.boop.params.message.description.discord_key)
    async def boop(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'boop', user, message)

    @app_commands.command(name=locale.fun.wave.name.discord_key, description=locale.fun.wave.description.discord_key)
    @app_commands.describe(user=locale.fun.wave.params.member.description.discord_key, message=locale.fun.wave.params.message.description.discord_key)
    async def wave(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'wave', user, message)

    @app_commands.command(name=locale.fun.slap.name.discord_key, description=locale.fun.slap.description.discord_key)
    @app_commands.describe(user=locale.fun.slap.params.member.description.discord_key, message=locale.fun.slap.params.message.description.discord_key)
    async def slap(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'slap', user, message)

    @app_commands.command(name=locale.fun.laugh.name.discord_key, description=locale.fun.laugh.description.discord_key)
    @app_commands.describe(user=locale.fun.laugh.params.member.description.discord_key, message=locale.fun.laugh.params.message.description.discord_key)
    async def laugh(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'laugh', user, message)

    @app_commands.command(name=locale.fun.tickle.name.discord_key, description=locale.fun.tickle.description.discord_key)
    @app_commands.describe(user=locale.fun.tickle.params.member.description.discord_key, message=locale.fun.tickle.params.message.description.discord_key)
    async def tickle(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'tickle', user, message)

    @app_commands.command(name=locale.fun.pat.name.discord_key, description=locale.fun.pat.description.discord_key)
    @app_commands.describe(user=locale.fun.pat.params.member.description.discord_key, message=locale.fun.pat.params.message.description.discord_key)
    async def pat(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'pat', user, message)

    @app_commands.command(name=locale.fun.poke.name.discord_key, description=locale.fun.poke.description.discord_key)
    @app_commands.describe(user=locale.fun.poke.params.member.description.discord_key, message=locale.fun.poke.params.message.description.discord_key)
    async def poke(self, interaction: discord.Interaction, user: discord.Member, message: app_commands.Range[str, 0, 2000]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await fun_command(command_info, 'poke', user, message)

class FunCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        utility_cmds = FunCommands(name=locale.funcmd.name.discord_key, description=locale.funcmd.description.discord_key)
        if self.bot.tree:
            self.bot.tree.add_command(utility_cmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FunCog(bot))
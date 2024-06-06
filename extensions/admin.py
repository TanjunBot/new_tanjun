import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.admin.addrole import addrole as addroleCommand
from commands.admin.removerole import removerole as removeroleCommand
from commands.admin.createrole import createrole as createroleCommand

class administrationCommands(discord.app_commands.Group):
    @app_commands.command(name="addrole", description="Add a role to a user")
    @app_commands.describe(user="The user to add the role to")
    @app_commands.describe(role="The role to add")
    async def addrole(self, ctx, user: discord.Member, role: discord.Role):
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

        await addroleCommand(commandInfo=commandInfo, target=user, role=role)
        return

    @app_commands.command(name="removerole", description="Remove a role from a user")
    @app_commands.describe(user="The user to remove the role from")
    @app_commands.describe(role="The role to remove")
    async def removerole(self, ctx, user: discord.Member, role: discord.Role):
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

        await removeroleCommand(commandInfo=commandInfo, target=user, role=role)
        return
    
    @app_commands.command(name="createrole", description="Create a role")
    @app_commands.describe(name = "The name of the role")
    @app_commands.describe(color = "The color of the role")
    async def createrole(self, ctx, name: str, color: str = None, display_icon: discord.Attachment = None, hoist: bool = False, mentionable: bool = False, reason: str = None, display_emoji: str = None):
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

        await createroleCommand(commandInfo=commandInfo, name=name, color=color, display_icon=display_icon if display_icon else display_emoji, hoist=hoist, mentionable=mentionable, reason=reason)
        return


class adminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addrole(self, ctx, **args) -> None:
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )
        
        target: discord.Member = ctx.message.mentions

        if(len(target) == 0):
            await ctx.reply(tanjunLocalizer.localize(locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US", key="commands.admin.addrole.noUser"))
            return
        
        role: discord.Role = ctx.message.role_mentions
        if(len(role) == 0):
            await ctx.reply(tanjunLocalizer.localize(locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US", key="commands.admin.addrole.noRole"))
            return
        for t in target:
            for r in role:
                await addroleCommand(commandInfo=commandInfo, target=t, role=r)
        return
    
    @commands.command()
    async def removerole(self, ctx) -> None:
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        target = ctx.message.mentions
        if(len(target) == 0):
            await ctx.reply(tanjunLocalizer.localize(locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US", key="commands.admin.removerole.noUser"))
            return
        
        role = ctx.message.role_mentions
        if(len(role) == 0):
            await ctx.reply(tanjunLocalizer.localize(locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US", key="commands.admin.removerole.noRole"))
            return
        
        for t in target:
            for r in role:
                await removeroleCommand(commandInfo=commandInfo, target=t, role=r)

        return
    
    @commands.command()
    async def createrole(self, ctx) -> None:
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await createroleCommand(commandInfo=commandInfo, name="Test")
        return

    @commands.Cog.listener()
    async def on_ready(self):
        admincmds = administrationCommands(
            name="admin", description="Administriere den Server"
        )
        self.bot.tree.add_command(admincmds)


async def setup(bot):
    await bot.add_cog(adminCog(bot))

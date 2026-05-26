from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

import utility
from commands.fun.funcommands import fun_command

FUN_ACTIONS = ["hug", "kiss", "boop", "wave", "slap", "laugh", "tickle", "pat", "poke"]


class funCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("fun_action_name"),
        description=app_commands.locale_str("fun_action_description"),
    )
    @app_commands.describe(
        action=app_commands.locale_str("fun_action_params_action_description"),
        user=app_commands.locale_str("fun_action_params_member_description"),
        message=app_commands.locale_str("fun_action_params_message_description"),
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name=app_commands.locale_str(f"fun_action_choice_{action}"), value=action)
            for action in FUN_ACTIONS
        ]
    )
    async def action(
        self,
        interaction: discord.Interaction,
        action: str,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,  # type: ignore[arg-type]
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await fun_command(commandInfo, action, user, message)


class funCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        utilityCmds = funCommands(
            name=app_commands.locale_str("funcmd_name"), description=app_commands.locale_str("funcmd_description")
        )
        if self.bot.tree:  # type: ignore[truthy-bool]
            self.bot.tree.add_command(utilityCmds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(funCog(bot))

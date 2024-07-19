import discord
from discord.ext import commands, tasks
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List
from api import getCustomSituations

from commands.ai.add_custom_situation import add_custom_situation
from commands.ai.delete_custom_situation import delete_custom_situation

async def aiCustomSituationAutocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    
    situations = await getCustomSituations()

    filtered_situations = [
        situation for situation in situations if current.lower() in situation.lower()
    ]

    return [
        app_commands.Choice(name=situation, value=situation)
        for situation in filtered_situations[:25]
    ]

class CustomSituationCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("ai_createcustom_name"),
        description=app_commands.locale_str("ai_createcustom_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("ai_createcustom_name"),
        personality=app_commands.locale_str("ai_createcustom_personality_description"),
        temperature=app_commands.locale_str("ai_createcustom_temperature_description"),
        top_p=app_commands.locale_str("ai_createcustom_topp_description"),
        frequency_penalty=app_commands.locale_str("ai_createcustom_frequencypenalty_description"),
        presence_penalty=app_commands.locale_str("ai_createcustom_presencepenalty_description"),
    )
    async def add_custom(
        self,
        ctx: discord.Interaction,
        name: app_commands.Range[str, 3, 15],
        personality: app_commands.Range[str, 10, 4000],
        temperature: app_commands.Range[float, 0, 2] = 1,
        top_p: app_commands.Range[float, 0, 1] = 1,
        frequency_penalty: app_commands.Range[float, 0, 2] = 0,
        presence_penalty: app_commands.Range[float, 0, 2] = 0,
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

        await add_custom_situation(
            commandInfo=commandInfo,
            name=name,
            situation=personality,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

    @app_commands.command(
        name=app_commands.locale_str("ai_deletecustom_name"),
        description=app_commands.locale_str("ai_deletecustom_description"),
    )
    async def delete_custom(
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

        await delete_custom_situation(
            commandInfo=commandInfo,
        )

class AiCommands(discord.app_commands.Group):
    ...

class AiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):  
        aicmds = AiCommands(name="ai", description="✨POGGERS✨")
        aicmds.add_command(CustomSituationCommands(name="custom_situations", description="Create and manage your custom situation"))
        self.bot.tree.add_command(aicmds)



async def setup(bot):
    await bot.add_cog(AiCog(bot))

import discord
from discord.ext import commands
from discord import app_commands
import utility
from typing import List

from commands.ai.add_custom_situation import add_custom_situation
from commands.ai.delete_custom_situation import delete_custom_situation
from commands.ai.ask_gpt import ask_gpt
from api import getCustomSituations, getCustomSituation

async def aiCustomSituationAutocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    
    print("Autocomplete triggered with current: ", current)
    
    situations = await getCustomSituations()

    print("Situations fetched: ", situations)

    filtered_situations = [
        situation for situation in situations if current.lower() in situation.lower()
    ]

    return [
        app_commands.Choice(name=situation, value=situation)
        for situation in filtered_situations[:25]
    ]

class CustomSituationCommands(discord.app_commands.Group):
    @app_commands.command(
        name="createcustom",
        description="Create a custom situation"
    )
    @app_commands.describe(
        name="The name of the custom situation",
        personality="The personality description",
        temperature="The temperature setting",
        top_p="The top_p setting",
        frequency_penalty="The frequency penalty setting",
        presence_penalty="The presence penalty setting",
    )
    async def add_custom(
        self,
        interaction: discord.Interaction,
        name: app_commands.Range[str, 3, 15],
        personality: app_commands.Range[str, 10, 4000],
        temperature: app_commands.Range[float, 0, 2] = 1,
        top_p: app_commands.Range[float, 0, 1] = 1,
        frequency_penalty: app_commands.Range[float, 0, 2] = 0,
        presence_penalty: app_commands.Range[float, 0, 2] = 0,
    ):
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await interaction.response.defer()

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
        name="deletecustom",
        description="Delete a custom situation"
    )
    async def delete_custom(
        self,
        interaction: discord.Interaction,
    ):
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await interaction.response.defer()

        await delete_custom_situation(
            commandInfo=commandInfo,
        )

class AiCommands(discord.app_commands.Group):
    @app_commands.command(
        name="askcustom",
        description="Ask a custom situation"
    )
    @app_commands.describe(
        prompt="The prompt for the custom situation",
        personality="The personality description",
    )
    @app_commands.autocomplete(personality=aiCustomSituationAutocomplete)
    async def ask_custom_situation(self, interaction: discord.Interaction, prompt: app_commands.Range[str, 1, 1000], personality: str):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        situation = await getCustomSituation(personality)

        await ask_gpt(commandInfo, name=personality, situation=situation[1], prompt=prompt, temperature=situation[4], top_p=situation[5], frequency_penalty=situation[6], presence_penalty=situation[7])

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

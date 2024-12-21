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
    situations = await getCustomSituations()
    filtered_situations = [
        situation[0] for situation in situations if current.lower() in situation[0].lower()
    ]

    return [
        app_commands.Choice(name=situation, value=situation)
        for situation in filtered_situations[:25]
    ]

class CustomSituationCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("ai_createcustom_name"),
        description=app_commands.locale_str("ai_createcustom_description")
    )
    @app_commands.describe(
        name=app_commands.locale_str("ai_createcustom_params_name_description"),
        personality=app_commands.locale_str("ai_createcustom_params_personality_description"),
        temperature=app_commands.locale_str("ai_createcustom_params_temperature_description"),
        top_p=app_commands.locale_str("ai_createcustom_params_top_p_description"),
        frequency_penalty=app_commands.locale_str("ai_createcustom_params_frequency_penalty_description"),
        presence_penalty=app_commands.locale_str("ai_createcustom_params_presence_penalty_description"),
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
        name=app_commands.locale_str("ai_deletecustom_name"),
        description=app_commands.locale_str("ai_deletecustom_description")
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
        name=app_commands.locale_str("ai_askcustom_name"),
        description=app_commands.locale_str("ai_askcustom_description")
    )
    @app_commands.describe(
        prompt=app_commands.locale_str("ai_askcustom_params_prompt_description"),
        personality=app_commands.locale_str("ai_askcustom_params_personality_description"),
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
    
    @app_commands.command(
        name=app_commands.locale_str("ai_askgpt_name"),
        description=app_commands.locale_str("ai_askgpt_description")
    )
    @app_commands.describe(
        prompt=app_commands.locale_str("ai_askgpt_params_prompt_description"),
        temperature=app_commands.locale_str("ai_askgpt_params_temperature_description"),
        top_p=app_commands.locale_str("ai_askgpt_params_top_p_description"),
        frequency_penalty=app_commands.locale_str("ai_askgpt_params_frequency_penalty_description"),
        presence_penalty=app_commands.locale_str("ai_askgpt_params_presence_penalty_description"),
    )
    async def ask_gpt_command(  
            self, 
            interaction: discord.Interaction, 
            prompt: app_commands.Range[str, 1, 1000],
            temperature: app_commands.Range[float, 0, 2] = 1,
            top_p: app_commands.Range[float, 0, 1] = 1,
            frequency_penalty: app_commands.Range[float, 0, 2] = 0,
            presence_penalty: app_commands.Range[float, 0, 2] = 0,
        ):
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

        await ask_gpt(commandInfo, name="GPT", situation="", prompt=prompt, temperature=temperature, top_p=top_p, frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)

    @app_commands.command(
        name=app_commands.locale_str("ai_asktanjuwun_name"),
        description=app_commands.locale_str("ai_asktanjuwun_description")
    )
    @app_commands.describe(
        prompt=app_commands.locale_str("ai_asktanjuwun_params_prompt_description"),
        temperature=app_commands.locale_str("ai_asktanjuwun_params_temperature_description"),
        top_p=app_commands.locale_str("ai_asktanjuwun_params_top_p_description"),
        frequency_penalty=app_commands.locale_str("ai_asktanjuwun_params_frequency_penalty_description"),
        presence_penalty=app_commands.locale_str("ai_asktanjuwun_params_presence_penalty_description"),
    )
    async def ask_tanjuwun_command(  
            self, 
            interaction: discord.Interaction, 
            prompt: app_commands.Range[str, 1, 1000],
            temperature: app_commands.Range[float, 0, 2] = 1,
            top_p: app_commands.Range[float, 0, 1] = 1,
            frequency_penalty: app_commands.Range[float, 0, 2] = 0,
            presence_penalty: app_commands.Range[float, 0, 2] = 0,
        ):
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

        situation = f"""
        Your name is Tanjuwun. You are the Brother of Tanjun, the Discord Bot. You dont have Friends and watch Anime all day. You constantly use UwU, qwq, owo and talk in Anime uwu language. You also use many Unicode Emoticons. 
        Answer in the Locale: {interaction.locale}
        Information about the sener:
        name: {interaction.user} server: {interaction.guild} channel: {interaction.channel}
        """

        await ask_gpt(commandInfo, name="tanjuwun", situation=situation, prompt=prompt, temperature=temperature, top_p=top_p, frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)

class AiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        aicmds = AiCommands(name=app_commands.locale_str("ai_name"), description=app_commands.locale_str("ai_description"))
        aicmds.add_command(CustomSituationCommands(name=app_commands.locale_str("ai_customsituations_name"), description=app_commands.locale_str("ai_customsituations_description")))
        self.bot.tree.add_command(aicmds)

async def setup(bot):
    await bot.add_cog(AiCog(bot))

from __future__ import annotations
from locale_keys import locale
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.ai.add_custom_situation import add_custom_situation
from commands.ai.ask_gpt import ask_gpt
from commands.ai.delete_custom_situation import delete_custom_situation
from commands.ai.show_tokens import show_tokens
from services.ai_service import AiService

async def aiCustomSituationAutocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    situations = []
    async for name in AiService.get_public_situations_iterator():
        if current.lower() in name.lower():
            situations.append(name)
            if len(situations) >= 25:
                break
    return [app_commands.Choice(name=situation, value=situation) for situation in situations]

class CustomSituationCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.ai.createcustom.name.discord_key, description=locale.ai.createcustom.description.discord_key)
    @app_commands.describe(name=locale.ai.createcustom.params.name.description.discord_key, personality=locale.ai.createcustom.params.personality.description.discord_key, temperature=locale.ai.createcustom.params.temperature.description.discord_key, topp=locale.ai.createcustom.params.topp.description.discord_key, frequencypenalty=locale.ai.createcustom.params.frequencypenalty.description.discord_key, presencepenalty=locale.ai.createcustom.params.presencepenalty.description.discord_key)
    async def add_custom(self, interaction: discord.Interaction, name: app_commands.Range[str, 3, 15], personality: app_commands.Range[str, 10, 4000], temperature: app_commands.Range[float, 0, 2]=1, topp: app_commands.Range[float, 0, 1]=1, frequencypenalty: app_commands.Range[float, 0, 2]=0, presencepenalty: app_commands.Range[float, 0, 2]=0) -> None:
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await interaction.response.defer()
        await add_custom_situation(command_info=command_info, name=name, situation=personality, temperature=temperature, top_p=topp, frequency_penalty=frequencypenalty, presence_penalty=presencepenalty)

    @app_commands.command(name=locale.ai.deletecustom.name.discord_key, description=locale.ai.deletecustom.description.discord_key)
    async def delete_custom(self, interaction: discord.Interaction) -> None:
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await interaction.response.defer()
        await delete_custom_situation(command_info=command_info)

class AiCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.ai.askcustom.name.discord_key, description=locale.ai.askcustom.description.discord_key)
    @app_commands.describe(prompt=locale.ai.askcustom.params.prompt.description.discord_key, personality=locale.ai.askcustom.params.personality.description.discord_key)
    @app_commands.autocomplete(personality=aiCustomSituationAutocomplete)
    async def ask_custom_situation(self, interaction: discord.Interaction, prompt: app_commands.Range[str, 1, 1000], personality: str) -> None:
        await interaction.response.defer()
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        situation = await AiService.get_situation(personality, require_unlocked=True)
        await ask_gpt(command_info, name=personality, situation=situation.situation if situation else '', prompt=prompt, temperature=situation.temperature if situation else 1.0, top_p=situation.top_p if situation else 1.0, frequency_penalty=situation.frequency_penalty if situation else 0.0, presence_penalty=situation.presence_penalty if situation else 0.0)

    @app_commands.command(name=locale.ai.askgpt.name.discord_key, description=locale.ai.askgpt.description.discord_key)
    @app_commands.describe(prompt=locale.ai.askgpt.params.prompt.description.discord_key, temperature=locale.ai.askgpt.params.temperature.description.discord_key, topp=locale.ai.askgpt.params.topp.description.discord_key, frequencypenalty=locale.ai.askgpt.params.frequencypenalty.description.discord_key, presencepenalty=locale.ai.askgpt.params.presencepenalty.description.discord_key)
    async def ask_gpt_command(self, interaction: discord.Interaction, prompt: app_commands.Range[str, 1, 1000], temperature: app_commands.Range[float, 0, 2]=1, topp: app_commands.Range[float, 0, 1]=1, frequencypenalty: app_commands.Range[float, 0, 2]=0, presencepenalty: app_commands.Range[float, 0, 2]=0) -> None:
        await interaction.response.defer()
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await ask_gpt(command_info, name='GPT', situation='', prompt=prompt, temperature=temperature, top_p=topp, frequency_penalty=frequencypenalty, presence_penalty=presencepenalty)

    @app_commands.command(name=locale.ai.asktanjuwun.name.discord_key, description=locale.ai.asktanjuwun.description.discord_key)
    @app_commands.describe(prompt=locale.ai.asktanjuwun.params.prompt.description.discord_key, temperature=locale.ai.asktanjuwun.params.temperature.description.discord_key, topp=locale.ai.asktanjuwun.params.topp.description.discord_key, frequencypenalty=locale.ai.asktanjuwun.params.frequencypenalty.description.discord_key, presencepenalty=locale.ai.asktanjuwun.params.presencepenalty.description.discord_key)
    async def ask_tanjuwun_command(self, interaction: discord.Interaction, prompt: app_commands.Range[str, 1, 1000], temperature: app_commands.Range[float, 0, 2]=1, topp: app_commands.Range[float, 0, 1]=1, frequencypenalty: app_commands.Range[float, 0, 2]=0, presencepenalty: app_commands.Range[float, 0, 2]=0) -> None:
        await interaction.response.defer()
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        situation = f'\n        Your name is Tanjuwun. You are the Brother of Tanjun, the Discord Bot. You dont have Friends and watch Anime all day. You constantly use UwU, qwq, owo and talk in Anime uwu language. You also use many Unicode Emoticons.\n        Answer in the Locale: {interaction.locale}\n        Information about the sener:\n        name: {interaction.user} server: {interaction.guild} channel: {interaction.channel}\n        '
        await ask_gpt(command_info, name='tanjuwun', situation=situation, prompt=prompt, temperature=temperature, top_p=topp, frequency_penalty=frequencypenalty, presence_penalty=presencepenalty)

    @app_commands.command(name=locale.ai.tokens.name.discord_key, description=locale.ai.tokens.description.discord_key)
    async def tokens_command(self, interaction: discord.Interaction) -> None:
        from typing import cast
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await show_tokens(command_info)

class AiCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        aicmds = AiCommands(name=locale.ai.name.discord_key, description=locale.ai.description.discord_key)
        aicmds.add_command(CustomSituationCommands(name=locale.ai.customsituations.name.discord_key, description=locale.ai.customsituations.description.discord_key))
        if self.bot.tree:
            self.bot.tree.add_command(aicmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AiCog(bot))
from locale_keys import locale
import discord
from discord import ui
from api import feedbackIsBlocked
from utility import CommandInfo, EmbedColor, tanjunEmbed

class FeedbackModal(ui.Modal):

    def __init__(self, command_info: CommandInfo, title: str, description: str) -> None:
        self.command_info = command_info
        self.title = title
        self.description = description
        super().__init__(timeout=6000)
        self.add_item(ui.TextInput(label=locale.commands.utility.feedback.modal.feedbacktitle.label(self.command_info.locale), placeholder=locale.commands.utility.feedback.modal.feedbacktitle.placeholder(self.command_info.locale), min_length=5, max_length=100, required=True))
        self.add_item(ui.TextInput(label=locale.commands.utility.feedback.modal.feedbackdescription.label(self.command_info.locale), placeholder=locale.commands.utility.feedback.modal.feedbackdescription.placeholder(self.command_info.locale), min_length=5, max_length=2048, required=True, style=discord.TextStyle.paragraph))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.utility.feedback.modal.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_submit(self, interaction: discord.Interaction) -> None:
        feedback_channel = self.command_info.client.get_channel(1266385101512773773)
        if not isinstance(feedback_channel, discord.TextChannel):
            return
        from typing import cast
        title_item = cast(discord.ui.TextInput[discord.ui.Modal], self.children[0])
        desc_item = cast(discord.ui.TextInput[discord.ui.Modal], self.children[1])
        feedback_title = title_item.value
        feedback_description = desc_item.value
        embed = tanjunEmbed(title=feedback_title, description=feedback_description)
        await feedback_channel.send(embed=embed, content=f'{interaction.user.name} ({interaction.user.id}) hat ein Feedback abgegeben\n<@&1152916080986161225>')
        embed = tanjunEmbed(colour=EmbedColor.SUCCESS, title=locale.commands.utility.feedback.modal.submitted.title(self.command_info.locale), description=locale.commands.utility.feedback.modal.submitted.description(self.command_info.locale))
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def feedback(command_info: CommandInfo, ctx: discord.Interaction) -> None:
    if await feedbackIsBlocked(command_info.user.id):
        embed = tanjunEmbed(title=locale.commands.utility.feedback.blocked.title(str(command_info.locale)), description=locale.commands.utility.feedback.blocked.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    modal = FeedbackModal(command_info=command_info, title=locale.commands.utility.feedback.modal.title(command_info.locale), description=locale.commands.utility.feedback.modal.description(command_info.locale))
    await ctx.response.send_modal(modal)
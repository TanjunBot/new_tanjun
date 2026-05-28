import discord
from discord import ui

from api import feedbackIsBlocked
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


class FeedbackModal(ui.Modal):
    def __init__(self, command_info: CommandInfo, title: str, description: str) -> None:
        self.command_info = command_info
        self.title = title
        self.description = description
        super().__init__(timeout=6000)

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.feedback.modal.feedbacktitle.label",
                ),
                placeholder=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.feedback.modal.feedbacktitle.placeholder",
                ),
                min_length=5,
                max_length=100,
                required=True,
            )
        )

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.feedback.modal.feedbackdescription.label",
                ),
                placeholder=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.feedback.modal.feedbackdescription.placeholder",
                ),
                min_length=5,
                max_length=2048,
                required=True,
                style=discord.TextStyle.paragraph,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.utility.feedback.modal.not_authorized",
                ),
                ephemeral=True,
            )
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
        embed = tanjunEmbed(
            title=feedback_title,
            description=feedback_description,
        )
        await feedback_channel.send(
            embed=embed,
            content=f"{interaction.user.name} ({interaction.user.id}) hat ein Feedback abgegeben\n<@&1152916080986161225>",
        )

        embed = tanjunEmbed(
            colour=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.feedback.modal.submitted.title",
            ),
            description=tanjunLocalizer.localize(
                self.command_info.locale,
                "commands.utility.feedback.modal.submitted.description",
            ),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def feedback(command_info: CommandInfo, ctx: discord.Interaction) -> None:
    if await feedbackIsBlocked(command_info.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.feedback.blocked.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.feedback.blocked.description"),
        )
        await command_info.reply(embed=embed)
        return
    modal = FeedbackModal(
        command_info=command_info,
        title=tanjunLocalizer.localize(command_info.locale, "commands.utility.feedback.modal.title"),
        description=tanjunLocalizer.localize(command_info.locale, "commands.utility.feedback.modal.description"),
    )

    await ctx.response.send_modal(modal)

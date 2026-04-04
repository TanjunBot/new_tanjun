import discord
from discord import ui

from api import feedbackIsBlocked
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


class feedbackModal(ui.Modal):
    def __init__(self, commandInfo: CommandInfo, title: str, description: str) -> None:
        self.commandInfo = commandInfo
        self.title = title
        self.description = description
        super().__init__(timeout=6000)

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.utility.feedback.modal.feedbacktitle.label",
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
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
                    self.commandInfo.locale,
                    "commands.utility.feedback.modal.feedbackdescription.label",
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.utility.feedback.modal.feedbackdescription.placeholder",
                ),
                min_length=5,
                max_length=2048,
                required=True,
                style=discord.TextStyle.paragraph,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.utility.feedback.modal.not_authorized",
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_submit(self, interaction: discord.Interaction) -> None:
        feedbackChannel = self.commandInfo.client.get_channel(1266385101512773773)
        if not isinstance(feedbackChannel, discord.TextChannel):
            return
        from typing import cast

        title_item = cast(discord.ui.TextInput[discord.ui.Modal], self.children[0])
        desc_item = cast(discord.ui.TextInput[discord.ui.Modal], self.children[1])
        feedbackTitle = title_item.value
        feedbackDescription = desc_item.value
        embed = tanjunEmbed(
            title=feedbackTitle,
            description=feedbackDescription,
        )
        await feedbackChannel.send(
            embed=embed,
            content=f"{interaction.user.name} ({interaction.user.id}) hat ein Feedback abgegeben\n<@&1152916080986161225>",
        )

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.utility.feedback.modal.submitted.title",
            ),
            description=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.utility.feedback.modal.submitted.description",
            ),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def feedback(commandInfo: CommandInfo, ctx: discord.Interaction) -> None:
    if await feedbackIsBlocked(commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.feedback.blocked.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.feedback.blocked.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    modal = feedbackModal(
        commandInfo=commandInfo,
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.feedback.modal.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.feedback.modal.description"),
    )

    await ctx.response.send_modal(modal)

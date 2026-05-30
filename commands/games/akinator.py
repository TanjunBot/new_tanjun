from typing import Any

import discord
from akinator_python import Akinator  # type: ignore[import-not-found]

import utility
from localizer import tanjunLocalizer


# Valid Themes: "Characters"; "Animals", "Objects"
async def akinator(command_info: utility.CommandInfo, theme: str | None = None) -> None:
    language = "en"
    if str(command_info.locale) == "en" or str(command_info.locale) == "en-US" or str(command_info.locale) == "en-GB":
        language = "en"
    elif str(command_info.locale) == "de":
        language = "de"
    elif str(command_info.locale) == "ar":
        language = "ar"
    elif str(command_info.locale) in ["zh-CN", "zh-TW"]:
        language = "zh"
    elif str(command_info.locale) in ["es", "es-ES", "es-419"]:
        language = "es"
    elif str(command_info.locale) == "fr":
        language = "fr"
    elif str(command_info.locale) == "he":
        language = "he"
    elif str(command_info.locale) == "it":
        language = "it"
    elif str(command_info.locale) == "ja":
        language = "jp"
    elif str(command_info.locale) == "ko":
        language = "ko"
    elif str(command_info.locale) == "nl":
        language = "nl"
    elif str(command_info.locale) == "pl":
        language = "pl"
    elif str(command_info.locale) in ["pt-PT", "pt", "pt-BR"]:
        language = "pt"
    elif str(command_info.locale) == "ru":
        language = "ru"
    elif str(command_info.locale) == "tr":
        language = "tr"
    elif str(command_info.locale) == "id":
        language = "id"

    aki = Akinator(lang=language, child_mode=True, theme=theme)
    aki.start_game()

    class AkinatorView(discord.ui.View):
        def __init__(self, ci: utility.CommandInfo) -> None:
            super().__init__()
            self.command_info = ci

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.yes"),
            style=discord.ButtonStyle.success,
            custom_id="akinator_yes",
            emoji="✅",
        )
        async def akinator_yes(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.defer()
            await update_embed(interaction, "y")

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.no"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_no",
            emoji="❌",
        )
        async def akinator_no(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.defer()
            if interaction.user.id != self.command_info.user.id:  # type: ignore[misc]
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "n")

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.idk"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_idk",
            emoji="❔",
        )
        async def akinator_idk(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.defer()
            if interaction.user.id != self.command_info.user.id:  # type: ignore[misc]
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "idk")

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.probably"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_probably",
            emoji="🤔",
        )
        async def akinator_probably(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.defer()
            if interaction.user.id != self.command_info.user.id:  # type: ignore[misc]
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "p")

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.probably_not"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_probably_not",
            emoji="🤨",
        )
        async def akinator_probably_not(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.defer()
            if interaction.user.id != self.command_info.user.id:  # type: ignore[misc]
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "pn")

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.back"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_back",
            emoji="🔙",
        )
        async def akinator_back(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.defer()
            if interaction.user.id != self.command_info.user.id:  # type: ignore[misc]
                await interaction.followup.send(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "b")

    def answer_to_locale_string(answer: str) -> None:
        if answer == "y":
            return tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.yes")  # type: ignore[return-value]
        elif answer == "n":
            return tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.no")  # type: ignore[return-value]
        elif answer == "idk":
            return tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.idk")  # type: ignore[return-value]
        elif answer == "p":
            return tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.probably")  # type: ignore[return-value]
        elif answer == "pn":
            return tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.probably_not")  # type: ignore[return-value]
        elif answer == "end":
            return tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.end")  # type: ignore[return-value]
        else:
            return tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.no_answer")  # type: ignore[return-value]

    async def update_embed(interaction: discord.Interaction, answer: str) -> None:
        if answer == "b":
            aki.go_back()
        else:
            aki.post_answer(answer)

        next_question = aki.question

        if aki.answer_id:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.akinator.result",
                    guess_name=aki.name,
                    guess_description=aki.description,
                    steps=aki.step,
                ),
            )
            embed.set_image(url=aki.photo)
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=None)  # type: ignore[union-attr]
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.akinator.description",
                    question=next_question,
                    lastAnswer=answer_to_locale_string(answer),  # type: ignore[func-returns-value]
                    progress=int(aki.progression),
                ),
            )
            embed.set_image(url=aki.akitude)
            await interaction.followup.edit_message(
                message_id=interaction.message.id, embed=embed, view=AkinatorView(command_info)
            )  # type: ignore[union-attr]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.games.akinator.description",
            question=aki.question,
            lastAnswer=tanjunLocalizer.localize(str(command_info.locale), "commands.games.akinator.no_answer"),
            progress=int(aki.progression),
        ),
    )
    embed.set_image(url=aki.akitude)

    await command_info.reply(embed=embed, view=AkinatorView(command_info))

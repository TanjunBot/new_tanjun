import discord
from akinator_python import Akinator

import utility
from localizer import tanjunLocalizer


# Valid Themes: "Characters"; "Animals", "Objects"
async def akinator(commandInfo: utility.commandInfo, theme: str = None):
    language = "en"
    if str(commandInfo.locale) == "en" or str(commandInfo.locale) == "en-US" or str(commandInfo.locale) == "en-GB":
        language = "en"
    elif str(commandInfo.locale) == "de":
        language = "de"
    elif str(commandInfo.locale) == "ar":
        language = "ar"
    elif str(commandInfo.locale) in ["zh-CN", "zh-TW"]:
        language = "zh"
    elif str(commandInfo.locale) in ["es", "es-ES", "es-419"]:
        language = "es"
    elif str(commandInfo.locale) == "fr":
        language = "fr"
    elif str(commandInfo.locale) == "he":
        language = "he"
    elif str(commandInfo.locale) == "it":
        language = "it"
    elif str(commandInfo.locale) == "ja":
        language = "jp"
    elif str(commandInfo.locale) == "ko":
        language = "ko"
    elif str(commandInfo.locale) == "nl":
        language = "nl"
    elif str(commandInfo.locale) == "pl":
        language = "pl"
    elif str(commandInfo.locale) in ["pt-PT", "pt", "pt-BR"]:
        language = "pt"
    elif str(commandInfo.locale) == "ru":
        language = "ru"
    elif str(commandInfo.locale) == "tr":
        language = "tr"
    elif str(commandInfo.locale) == "id":
        language = "id"

    aki = Akinator(lang=language, child_mode=True, theme=theme)
    aki.start_game()

    class AkinatorView(discord.ui.View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.yes"),
            style=discord.ButtonStyle.success,
            custom_id="akinator_yes",
            emoji="✅",
        )
        async def akinator_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            await update_embed(interaction, "y")

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.no"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_no",
            emoji="❌",
        )
        async def akinator_no(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "n")

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.idk"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_idk",
            emoji="❔",
        )
        async def akinator_idk(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "idk")

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.probably"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_probably",
            emoji="🤔",
        )
        async def akinator_probably(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "p")

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.probably_not"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_probably_not",
            emoji="🤨",
        )
        async def akinator_probably_not(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "pn")

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.back"),
            style=discord.ButtonStyle.secondary,
            custom_id="akinator_back",
            emoji="🔙",
        )
        async def akinator_back(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.notYourGame"),
                    ephemeral=True,
                )
                return
            await update_embed(interaction, "b")

    def answer_to_locale_string(answer: str):
        if answer == "y":
            return tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.yes")
        elif answer == "n":
            return tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.no")
        elif answer == "idk":
            return tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.idk")
        elif answer == "p":
            return tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.probably")
        elif answer == "pn":
            return tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.probably_not")
        elif answer == "end":
            return tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.end")
        else:
            return tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.no_answer")

    async def update_embed(interaction: discord.Interaction, answer: str):
        if answer == "b":
            aki.go_back()
        else:
            aki.post_answer(answer)

        next_question = aki.question

        if aki.answer_id:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.akinator.result",
                    guess_name=aki.name,
                    guess_description=aki.description,
                    steps=aki.step,
                ),
            )
            embed.set_image(url=aki.photo)
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=None)
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.akinator.description",
                    question=next_question,
                    lastAnswer=answer_to_locale_string(answer),
                    progress=int(aki.progression),
                ),
            )
            embed.set_image(url=aki.akitude)
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=AkinatorView())

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.games.akinator.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.akinator.description",
            question=aki.question,
            lastAnswer="No Answer",
            progress=int(aki.progression),
        ),
    )
    embed.set_image(url=aki.akitude)

    await commandInfo.reply(embed=embed, view=AkinatorView())

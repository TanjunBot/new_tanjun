import utility
import discord
from localizer import tanjunLocalizer
import random
from commands.games.country_flags.flags import random_flag
import difflib


async def flag_quiz(commandInfo: utility.commandInfo):
    locale = str(commandInfo.locale)
    flag_file = random_flag()
    correct_country = flag_file.replace(".png", "").replace("_", " ").title()
    correct_country = tanjunLocalizer.localize(locale, f"countries.{correct_country}")

    guesses = []
    hints_used = 0

    def get_similarity(guess: str, answer: str) -> float:
        return (
            difflib.SequenceMatcher(None, guess.lower(), answer.lower()).ratio() * 100
        )

    def get_hint(word: str) -> str:
        chars = list(word.lower())
        blanks = ["_"] * len(chars)
        # Show ~30% of letters randomly
        num_reveals = max(1, len(chars) // 3)
        reveal_positions = random.sample(range(len(chars)), num_reveals)
        for pos in reveal_positions:
            blanks[pos] = chars[pos]
        return "".join(blanks)

    async def update_game(
        interaction: discord.Interaction,
        given_up: bool = False,
        wrong_guess: bool = False,
        hint_used: bool = False,
    ):
        file = discord.File(
            f"commands/games/country_flags/{flag_file}", filename="flag.png"
        )

        if given_up:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.flagquiz.givenUp.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.flagquiz.givenUp.description",
                    country=correct_country,
                ),
            )
            embed.set_image(url="attachment://flag.png")
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                attachments=[file],
                view=None,
            )
            return

        if len(guesses) > 0 and guesses[-1].lower() == correct_country.lower():
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.flagquiz.success.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.flagquiz.success.description",
                    guesses=len(guesses),
                ),
            )
            embed.set_image(url="attachment://flag.png")
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                attachments=[file],
                view=None,
            )
            return

        if len(guesses) >= 5:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.flagquiz.failure.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.flagquiz.failure.description",
                    country=correct_country,
                ),
            )
            embed.set_image(url="attachment://flag.png")
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                attachments=[file],
                view=None,
            )
            return

        guess_list = ""
        for guess in guesses:
            similarity = get_similarity(guess, correct_country)
            guess_list += f"\n{guess} - {similarity:.1f}% similar"

        if hint_used:
            hint = get_hint(correct_country)
            guess_list += f"\n\n{tanjunLocalizer.localize(commandInfo.locale, 'commands.games.flagquiz.hint')}: `{hint}`"

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.games.flagquiz.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.games.flagquiz.description",
                remaining=5 - len(guesses),
                guesses=guess_list,
            ),
        )
        embed.set_image(url="attachment://flag.png")

        view = FlagQuizView(commandInfo)
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            embed=embed,
            attachments=[file],
            view=view,
        )

    class FlagQuizModal(discord.ui.Modal):
        def __init__(self, commandInfo: utility.commandInfo):
            super().__init__(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.flagquiz.modal.title"
                )
            )
            self.commandInfo = commandInfo

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.flagquiz.modal.input.label"
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.games.flagquiz.modal.input.placeholder",
                    ),
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            guess = self.children[0].value.strip()
            guesses.append(guess)
            await update_game(interaction)

    class FlagQuizView(discord.ui.View):
        def __init__(self, commandInfo: utility.commandInfo):
            super().__init__(timeout=3600)
            self.commandInfo = commandInfo

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.games.flagquiz.buttons.guess"
            ),
            style=discord.ButtonStyle.green,
        )
        async def guess_button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.flagquiz.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            modal = FlagQuizModal(self.commandInfo)
            await interaction.response.send_modal(modal)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.games.flagquiz.buttons.hint"
            ),
            style=discord.ButtonStyle.blurple,
        )
        async def hint_button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.flagquiz.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            nonlocal hints_used
            if hints_used == 0:
                hints_used += 1
                await update_game(interaction, hint_used=True)
            else:
                await interaction.followup.send(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.flagquiz.error.hintUsed"
                    ),
                    ephemeral=True,
                )

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.games.flagquiz.buttons.giveUp"
            ),
            style=discord.ButtonStyle.red,
        )
        async def give_up_button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.flagquiz.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            await update_game(interaction, given_up=True)

    view = FlagQuizView(commandInfo)
    file = discord.File(
        f"commands/games/country_flags/{flag_file}", filename="flag.png"
    )
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.games.flagquiz.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.flagquiz.initial.description",
            guesses="",
        ),
    )
    embed.set_image(url="attachment://flag.png")
    await commandInfo.reply(view=view, embed=embed, file=file)

import discord
import utility
from localizer import tanjunLocalizer
from api import get_giveaway, get_giveaway_participants
import random


async def reroll_giveaway(
    commandInfo: utility.commandInfo,
    giveawayId: int,
):
    if not commandInfo.permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    giveaway = await get_giveaway(giveawayId)
    if not giveaway:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.notFound.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if giveaway[1] != str(commandInfo.guild.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.notFound.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not giveaway[13]:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.notEnded.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.notEnded.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    class RerollOptionsView(discord.ui.View):
        def __init__(self, commandInfo: utility.commandInfo, giveawayId: int):
            super().__init__()
            self.commandInfo = commandInfo
            self.giveawayId = giveawayId

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.giveaway.reroll_giveaway.rerollOneWinner"
            ),
            style=discord.ButtonStyle.primary,
        )
        async def reroll_one(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.defer()
            await perform_reroll(self.commandInfo, self.giveawayId, 1)
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.giveaway.reroll_giveaway.rerollAllWinners"
            ),
            style=discord.ButtonStyle.primary,
        )
        async def reroll_all(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.defer()
            giveaway = await get_giveaway(self.giveawayId)
            await perform_reroll(self.commandInfo, self.giveawayId, giveaway[4])
            self.stop()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.commandInfo.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.giveaway.reroll_giveaway.error.notAuthorized",
                    ),
                    ephemeral=True,
                )
                return False
            return True

    winners_count = giveaway[4]
    if winners_count > 1:
        view = RerollOptionsView(commandInfo, giveawayId)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.selectOption.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.selectOption.description",
            ),
        )
        await commandInfo.reply(embed=embed, view=view)
    else:
        await perform_reroll(commandInfo, giveawayId, 1)


async def perform_reroll(
    commandInfo: utility.commandInfo, giveawayId: int, reroll_count: int
):
    participants = await get_giveaway_participants(giveawayId)

    if not participants:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.noParticipants.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.reroll_giveaway.error.noParticipants.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    new_winners = []
    for _ in range(min(reroll_count, len(participants))):
        if not participants:
            break
        # Nobody cares enough if the winner is choosen using a real(er) rng.
        # nosec: B311
        winner = random.choice(participants)
        new_winners.append(winner)
        participants.remove(winner)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.reroll_giveaway.success.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.reroll_giveaway.success.description",
            winners=", ".join(f"<@{winner}>" for winner in new_winners),
        ),
    )

    await commandInfo.reply(embed=embed)

    for winner in new_winners:
        member = commandInfo.guild.get_member(int(winner))
        if member:
            await member.send(
                tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.giveaway.reroll_giveaway.winnerDM",
                    guild_name=commandInfo.guild.name,
                )
            )

from locale_keys import locale
import random
import discord
import utility
from services.giveaway_service import giveaway_service

async def reroll_giveaway(command_info: utility.command_info, giveaway_id: int):
    if not command_info.permissions.manage_guild:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.error.missingPermission.title(command_info.locale), description=locale.commands.giveaway.reroll_giveaway.error.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    giveaway = await giveaway_service.get(giveaway_id)
    if not giveaway:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.error.notFound.title(command_info.locale), description=locale.commands.giveaway.reroll_giveaway.error.notFound.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if giveaway.guild_id != str(command_info.guild.id):
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.error.notFound.title(command_info.locale), description=locale.commands.giveaway.reroll_giveaway.error.notFound.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not giveaway.ended:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.error.notEnded.title(command_info.locale), description=locale.commands.giveaway.reroll_giveaway.error.notEnded.description(command_info.locale))
        await command_info.reply(embed=embed)
        return

    class RerollOptionsView(discord.ui.View):

        def __init__(self, command_info: utility.command_info, giveaway_id: int):
            super().__init__()
            self.command_info = command_info
            self.giveaway_id = giveaway_id

        @discord.ui.button(label=locale.commands.giveaway.reroll_giveaway.rerollOneWinner(command_info.locale), style=discord.ButtonStyle.primary)
        async def reroll_one(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            await perform_reroll(self.command_info, self.giveaway_id, 1)
            self.stop()

        @discord.ui.button(label=locale.commands.giveaway.reroll_giveaway.rerollAllWinners(command_info.locale), style=discord.ButtonStyle.primary)
        async def reroll_all(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            giveaway = await giveaway_service.get(self.giveaway_id)
            if giveaway is None:
                embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.error.notFound.title(self.command_info.locale), description=locale.commands.giveaway.reroll_giveaway.error.notFound.description(self.command_info.locale))
                await self.command_info.reply(embed=embed)
                self.stop()
                return
            await perform_reroll(self.command_info, self.giveaway_id, giveaway.winners)
            self.stop()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.command_info.user:
                await interaction.response.send_message(locale.commands.giveaway.reroll_giveaway.error.notAuthorized(self.command_info.locale), ephemeral=True)
                return False
            return True
    winners_count = giveaway.winners
    if winners_count > 1:
        view = RerollOptionsView(command_info, giveaway_id)
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.selectOption.title(command_info.locale), description=locale.commands.giveaway.reroll_giveaway.selectOption.description(command_info.locale))
        await command_info.reply(embed=embed, view=view)
    else:
        await perform_reroll(command_info, giveaway_id, 1)

async def perform_reroll(command_info: utility.command_info, giveaway_id: int, reroll_count: int):
    participants = await giveaway_service.get_participants(giveaway_id)
    if not participants:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.error.noParticipants.title(command_info.locale), description=locale.commands.giveaway.reroll_giveaway.error.noParticipants.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    new_winners = []
    for _ in range(min(reroll_count, len(participants))):
        if not participants:
            break
        winner = random.choice(participants)
        new_winners.append(winner)
        participants.remove(winner)
    embed = utility.tanjunEmbed(title=locale.commands.giveaway.reroll_giveaway.success.title(command_info.locale), description=locale.commands.giveaway.reroll_giveaway.success.description(command_info.locale, winners=', '.join((f'<@{winner}>' for winner in new_winners))))
    await command_info.reply(embed=embed)
    for winner in new_winners:
        member = command_info.guild.get_member(int(winner))
        if member:
            await member.send(locale.commands.giveaway.reroll_giveaway.winnerDM(command_info.locale, guild_name=command_info.guild.name))
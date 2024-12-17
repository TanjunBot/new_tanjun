import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List, Optional

from minigames.counting import counting
from minigames.countingChallenge import counting as countingChallenge
from minigames.countingmodes import counting as countingModes
from minigames.wordchain import wordchain
from minigames.addLevelXp import addLevelXp

from commands.giveaway.utility import add_giveaway_participant, addMessageToGiveaway
from loops.level import handleVoiceChange as handleLevelVoiceChange
from loops.giveaway import handleVoiceChange

from config import adminIds

from commands.ai.add_custom_situation_button_handler import approve_custom_situation, deny_custom_situation

from commands.utility.autopublish import publish_message
from commands.utility.afk import checkIfAfkHasToBeRemoved, checkIfMentionsAreAfk
from commands.utility.report import report_btn_click
from api import update_scheduled_message_content, remove_scheduled_message
from commands.admin.trigger_messages.send import send_trigger_message

from commands.admin.ticket.open_ticket import openTicket as openTicketListener
from commands.admin.ticket.close_ticket import close_ticket as closeTicketListener

class ListenerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await counting(message)
        await countingChallenge(message)
        await countingModes(message)
        await wordchain(message)
        await addLevelXp(message)
        await addMessageToGiveaway(message)
        await publish_message(message)
        await checkIfAfkHasToBeRemoved(message)
        await checkIfMentionsAreAfk(message)
        await send_trigger_message(message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            if interaction.data["custom_id"].startswith("giveaway_enter"):
                giveaway_id = interaction.data["custom_id"].split("; ")[1]
                embed = await add_giveaway_participant(giveawayid=giveaway_id, userid=interaction.user.id, client=self.bot)
                if embed:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            elif interaction.data["custom_id"].startswith("ai_add_custom_situation_approve"):
                if interaction.user.id not in adminIds:
                    return
                await approve_custom_situation(interaction)
            elif interaction.data["custom_id"].startswith("ai_add_custom_situation_deny"):
                if interaction.user.id not in adminIds:
                    return
                await deny_custom_situation(interaction)
            elif interaction.data["custom_id"].startswith("report_"):
                await report_btn_click(interaction, interaction.data["custom_id"])
                return
            elif interaction.data["custom_id"].startswith("ticket_create"):
                await openTicketListener(interaction)
                return
            elif interaction.data["custom_id"].startswith("ticket_close"):
                await closeTicketListener(interaction)
                return
        except:
            raise

    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        await handleVoiceChange(user, before, after)
        await handleLevelVoiceChange(user, before, after)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.reference:
            await update_scheduled_message_content(after.reference.message_id, after.content)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await remove_scheduled_message(message.id)

async def setup(bot):
    await bot.add_cog(ListenerCog(bot))

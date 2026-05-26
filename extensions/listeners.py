import discord
from discord.ext import commands

from api import remove_scheduled_message, update_scheduled_message_content
from commands.admin.joinToCreate.joinToCreateListener import memberJoin, memberLeave
from commands.admin.ticket.close_ticket import close_ticket as closeTicketListener
from commands.admin.ticket.open_ticket import openTicket as openTicketListener
from commands.admin.trigger_messages.send import send_trigger_message
from commands.ai.add_custom_situation_button_handler import (
    approve_custom_situation,
    deny_custom_situation,
)
from commands.channel.dynamicslowmode import dynamicslowmodeMessage
from commands.channel.farewell import farewellUser
from commands.channel.media import mediaChannelMessage
from commands.channel.welcome import welcomeNewUser
from commands.giveaway.utility import add_giveaway_participant, addMessageToGiveaway
from commands.utility.afk import checkIfAfkHasToBeRemoved, checkIfMentionsAreAfk
from commands.utility.autopublish import publish_message
from commands.utility.report import report_btn_click
from config import adminIds
from loops._voice_tracker import handleVoiceChange
from loops._voice_tracker import handleVoiceChange as handleLevelVoiceChange
from minigames.addLevelXp import addLevelXp
from minigames.counting import counting
from minigames.countingChallenge import counting as countingChallenge
from minigames.countingmodes import counting as countingModes
from minigames.wordchain import wordchain


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
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
        await mediaChannelMessage(message)
        await dynamicslowmodeMessage(message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        try:
            if not interaction.data:
                return
            custom_id = interaction.data.get("custom_id")
            if not isinstance(custom_id, str):
                return
            if custom_id.startswith("giveaway_enter"):
                giveaway_id = interaction.data["custom_id"].split("; ")[1]  # type: ignore[typeddict-item]
                embed = await add_giveaway_participant(  # type: ignore[func-returns-value]
                    giveawayid=giveaway_id,
                    userid=interaction.user.id,
                    client=self.bot,
                )
                if embed:
                    await interaction.response.send_message(embed=embed, ephemeral=True)  # type: ignore[unreachable]
            elif custom_id.startswith("ai_add_custom_situation_approve"):
                if interaction.user.id not in adminIds:
                    return
                await approve_custom_situation(interaction)
            elif custom_id.startswith("ai_add_custom_situation_deny"):
                if interaction.user.id not in adminIds:
                    return
                await deny_custom_situation(interaction)
            elif custom_id.startswith("report_"):
                await report_btn_click(interaction, custom_id)
                return
            elif custom_id.startswith("ticket_create"):
                await openTicketListener(interaction)
                return
            elif custom_id.startswith("ticket_close"):
                await closeTicketListener(interaction)
                return
        except Exception:
            logging.exception("Error in on_interaction listener")

    @commands.Cog.listener()
    async def on_voice_state_update(self, user: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        await memberLeave(before)
        await memberJoin(after, user)
        await handleVoiceChange(user, before, after)  # type: ignore[no-untyped-call]
        await handleLevelVoiceChange(user, before, after)  # type: ignore[no-untyped-call]

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if after.reference:
            await update_scheduled_message_content(after.reference.message_id, after.content)  # type: ignore[arg-type]

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        await remove_scheduled_message(message.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await welcomeNewUser(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        await farewellUser(member)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ListenerCog(bot))

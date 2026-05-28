import logging

import discord
from discord.ext import commands

from services.scheduled_message_service import ScheduledMessageService
from commands.admin.join_to_create.listener import memberJoin, memberLeave
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
from localizer import tanjunLocalizer
from loops._voice_tracker import handleVoiceChange
from minigames.add_level_xp import addLevelXp
from minigames.counting import counting
from minigames.counting_challenge import counting as countingChallenge
from minigames.counting_modes import counting as countingModes
from minigames.wordchain import wordchain


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Early filter: skip bot messages and DMs once for all handlers
        if message.author.bot:
            return
        if message.guild is None:
            return

        # Single DB check for all counting configs — skip all 3 handlers if none
        counting_config, challenge_config, modes_config = await get_counting_configs(message.channel.id)
        if counting_config:
            await counting(message, config=counting_config)
        if challenge_config:
            await countingChallenge(message, config=challenge_config)
        if modes_config:
            await countingModes(message, config=modes_config)
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
        except discord.Forbidden:
            locale = interaction.locale  # type: ignore[assignment]
            error_msg = tanjunLocalizer.localize(locale, "listeners.interaction.error.forbidden")
            await self._send_error(interaction, error_msg)
        except discord.NotFound:
            locale = interaction.locale  # type: ignore[assignment]
            error_msg = tanjunLocalizer.localize(locale, "listeners.interaction.error.notfound")
            await self._send_error(interaction, error_msg)
        except discord.HTTPException as e:
            locale = interaction.locale  # type: ignore[assignment]
            error_msg = tanjunLocalizer.localize(locale, "listeners.interaction.error.http", status=e.status)
            await self._send_error(interaction, error_msg)
        except Exception:
            logging.exception("Unexpected error in on_interaction listener")
            locale = interaction.locale  # type: ignore[assignment]
            error_msg = tanjunLocalizer.localize(locale, "listeners.interaction.error.unexpected")
            await self._send_error(interaction, error_msg)

    async def _send_error(self, interaction: discord.Interaction, message: str) -> None:
        embed = discord.Embed(
            colour=0xE74C3C,
            title="Error",
            description=message,
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            pass  # Truly give up if we can't even send an error

    @commands.Cog.listener()
    async def on_voice_state_update(self, user: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        await memberLeave(before)
        await memberJoin(after, user)
        await handleVoiceChange(user, before, after)  # type: ignore[no-untyped-call]

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if after.reference:
            # Update content of a scheduled message when the referenced message is edited.
            # after.reference.message_id is the scheduled message ID when the scheduled message
            # was sent via webhook/message reference.
            await ScheduledMessageService.update_content(after.reference.message_id, after.content)  # type: ignore[arg-type]

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        # NOTE: message.id is a Discord snowflake, not necessarily a scheduled message ID.
        # This only works if the deleted message happens to have the same ID as a
        # scheduled message entry — which is not generally the case.
        # A proper fix would require storing the message ID returned by the send
        # in the scheduled_messages table, then looking it up on delete.
        # For now we keep this best-effort behavior.
        await ScheduledMessageService.cancel(message.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await welcomeNewUser(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        await farewellUser(member)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ListenerCog(bot))

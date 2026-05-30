from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from extensions.listeners import ListenerCog
from tests.helpers.discord import make_guild, make_member, make_message, make_text_channel
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.listeners"


async def _cog() -> ListenerCog:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    return bot.cogs["ListenerCog"]


def _guild_message(*, author_bot: bool = False) -> MagicMock:
    msg = make_message()
    msg.author.bot = author_bot
    msg.guild = make_guild()
    msg.channel = make_text_channel(guild=msg.guild)
    return msg


class TestOnMessage:
    async def test_skips_bot_messages(self) -> None:
        cog = await _cog()
        with patch("extensions.listeners.run_handlers_sequential", new=AsyncMock()) as seq:
            await cog.on_message(_guild_message(author_bot=True))
            seq.assert_not_called()

    async def test_skips_dms(self) -> None:
        cog = await _cog()
        msg = make_message()
        msg.author.bot = False
        msg.guild = None
        with patch("extensions.listeners.run_handlers_sequential", new=AsyncMock()) as seq:
            await cog.on_message(msg)
            seq.assert_not_called()

    async def test_runs_counting_and_concurrent_handlers(self) -> None:
        cog = await _cog()
        msg = _guild_message()
        cfg = MagicMock()
        with (
            patch("extensions.listeners.get_counting_configs", new=AsyncMock(return_value=(cfg, cfg, cfg))),
            patch("extensions.listeners.run_handlers_sequential", new=AsyncMock()) as seq,
            patch("extensions.listeners.run_handlers_safe", new=AsyncMock()) as safe,
        ):
            await cog.on_message(msg)
            seq.assert_awaited_once()
            safe.assert_awaited_once()

    async def test_no_counting_configs(self) -> None:
        cog = await _cog()
        msg = _guild_message()
        with (
            patch("extensions.listeners.get_counting_configs", new=AsyncMock(return_value=(None, None, None))),
            patch("extensions.listeners.run_handlers_sequential", new=AsyncMock()) as seq,
            patch("extensions.listeners.run_handlers_safe", new=AsyncMock()) as safe,
        ):
            await cog.on_message(msg)
            seq.assert_awaited_once()
            assert seq.call_args[0][0] == []
            safe.assert_awaited_once()


class TestOnInteraction:
    def _interaction(self, custom_id: str, *, user_id: int = 111111111) -> MagicMock:
        ix = MagicMock()
        ix.data = {"custom_id": custom_id}
        ix.user = make_member(user_id=user_id)
        ix.response = MagicMock()
        ix.response.is_done = MagicMock(return_value=False)
        ix.response.send_message = AsyncMock()
        ix.followup = MagicMock()
        ix.followup.send = AsyncMock()
        ix.locale = "en-US"
        return ix

    async def test_no_data_returns_early(self) -> None:
        cog = await _cog()
        ix = MagicMock(data=None)
        await cog.on_interaction(ix)

    async def test_giveaway_enter(self) -> None:
        cog = await _cog()
        ix = self._interaction("giveaway_enter; gw123")
        embed = MagicMock()
        with patch("extensions.listeners.add_giveaway_participant", new=AsyncMock(return_value=embed)):
            await cog.on_interaction(ix)
        ix.response.send_message.assert_awaited_once()

    async def test_giveaway_enter_no_embed(self) -> None:
        cog = await _cog()
        ix = self._interaction("giveaway_enter; gw123")
        with patch("extensions.listeners.add_giveaway_participant", new=AsyncMock(return_value=None)):
            await cog.on_interaction(ix)

    async def test_ai_approve_admin(self) -> None:
        cog = await _cog()
        from config import adminIds

        admin_id = next(iter(adminIds))
        ix = self._interaction("ai_add_custom_situation_approve_x", user_id=admin_id)
        with patch("extensions.listeners.approve_custom_situation", new=AsyncMock()) as approve:
            await cog.on_interaction(ix)
            approve.assert_awaited_once()

    async def test_ai_approve_non_admin(self) -> None:
        cog = await _cog()
        ix = self._interaction("ai_add_custom_situation_approve_x", user_id=999999999)
        with patch("extensions.listeners.approve_custom_situation", new=AsyncMock()) as approve:
            await cog.on_interaction(ix)
            approve.assert_not_called()

    async def test_ai_deny_admin(self) -> None:
        cog = await _cog()
        from config import adminIds

        admin_id = next(iter(adminIds))
        ix = self._interaction("ai_add_custom_situation_deny_x", user_id=admin_id)
        with patch("extensions.listeners.deny_custom_situation", new=AsyncMock()) as deny:
            await cog.on_interaction(ix)
            deny.assert_awaited_once()

    async def test_report_button(self) -> None:
        cog = await _cog()
        ix = self._interaction("report_confirm_1")
        with patch("extensions.listeners.report_btn_click", new=AsyncMock()) as report:
            await cog.on_interaction(ix)
            report.assert_awaited_once()

    async def test_ticket_create_and_close(self) -> None:
        cog = await _cog()
        for cid, target in (
            ("ticket_create_1", "openTicketListener"),
            ("ticket_close_1", "closeTicketListener"),
        ):
            ix = self._interaction(cid)
            with patch(f"extensions.listeners.{target}", new=AsyncMock()) as handler:
                await cog.on_interaction(ix)
                handler.assert_awaited_once()

    async def test_forbidden_error(self) -> None:
        cog = await _cog()
        ix = self._interaction("report_x")
        with patch("extensions.listeners.report_btn_click", new=AsyncMock(side_effect=discord.Forbidden(MagicMock(), "x"))):
            await cog.on_interaction(ix)
        ix.response.send_message.assert_awaited_once()

    async def test_not_found_error(self) -> None:
        cog = await _cog()
        ix = self._interaction("report_x")
        with patch("extensions.listeners.report_btn_click", new=AsyncMock(side_effect=discord.NotFound(MagicMock(), "x"))):
            await cog.on_interaction(ix)

    async def test_http_exception_error(self) -> None:
        cog = await _cog()
        ix = self._interaction("report_x")
        err = discord.HTTPException(MagicMock(), "fail")
        err.status = 500
        with patch("extensions.listeners.report_btn_click", new=AsyncMock(side_effect=err)):
            await cog.on_interaction(ix)

    async def test_unexpected_error(self) -> None:
        cog = await _cog()
        ix = self._interaction("report_x")
        with patch("extensions.listeners.report_btn_click", new=AsyncMock(side_effect=RuntimeError("boom"))):
            await cog.on_interaction(ix)


class TestSendError:
    async def test_send_error_response_not_done(self) -> None:
        cog = await _cog()
        ix = MagicMock()
        ix.response.is_done = MagicMock(return_value=False)
        ix.response.send_message = AsyncMock()
        await cog._send_error(ix, "oops")

    async def test_send_error_response_done(self) -> None:
        cog = await _cog()
        ix = MagicMock()
        ix.response.is_done = MagicMock(return_value=True)
        ix.followup.send = AsyncMock()
        await cog._send_error(ix, "oops")

    async def test_send_error_failure_swallowed(self) -> None:
        cog = await _cog()
        ix = MagicMock()
        ix.response.is_done = MagicMock(return_value=False)
        ix.response.send_message = AsyncMock(side_effect=RuntimeError("fail"))
        await cog._send_error(ix, "oops")


class TestOtherListeners:
    async def test_voice_state_update(self) -> None:
        cog = await _cog()
        user = make_member()
        before = MagicMock()
        after = MagicMock()
        with (
            patch("extensions.listeners.memberLeave", new=AsyncMock()) as leave,
            patch("extensions.listeners.memberJoin", new=AsyncMock()) as join,
            patch("extensions.listeners.voice_user_manager.handle_voice_change", new=AsyncMock()) as voice,
        ):
            await cog.on_voice_state_update(user, before, after)
            leave.assert_awaited_once()
            join.assert_awaited_once()
            voice.assert_awaited_once()

    async def test_message_edit_updates_scheduled(self) -> None:
        cog = await _cog()
        before = make_message()
        after = make_message()
        after.reference = MagicMock(message_id=123)
        after.content = "edited"
        with patch("extensions.listeners.ScheduledMessageService.update_content", new=AsyncMock()) as update:
            await cog.on_message_edit(before, after)
            update.assert_awaited_once_with(123, "edited")

    async def test_message_edit_no_reference(self) -> None:
        cog = await _cog()
        before = make_message()
        after = make_message()
        after.reference = None
        with patch("extensions.listeners.ScheduledMessageService.update_content", new=AsyncMock()) as update:
            await cog.on_message_edit(before, after)
            update.assert_not_called()

    async def test_message_delete_cancels_scheduled(self) -> None:
        cog = await _cog()
        msg = make_message()
        scheduled = MagicMock(message_id="sched1")
        with (
            patch(
                "extensions.listeners.ScheduledMessageService.find_by_discord_message_id",
                new=AsyncMock(return_value=scheduled),
            ),
            patch("extensions.listeners.ScheduledMessageService.cancel", new=AsyncMock()) as cancel,
        ):
            await cog.on_message_delete(msg)
            cancel.assert_awaited_once_with("sched1")

    async def test_message_delete_no_scheduled(self) -> None:
        cog = await _cog()
        msg = make_message()
        with patch(
            "extensions.listeners.ScheduledMessageService.find_by_discord_message_id", new=AsyncMock(return_value=None)
        ):
            await cog.on_message_delete(msg)

    async def test_member_join(self) -> None:
        cog = await _cog()
        member = make_member()
        with patch("extensions.listeners.welcomeNewUser", new=AsyncMock()) as welcome:
            await cog.on_member_join(member)
            welcome.assert_awaited_once()

    async def test_member_remove(self) -> None:
        cog = await _cog()
        member = make_member()
        with patch("extensions.listeners.farewellUser", new=AsyncMock()) as farewell:
            await cog.on_member_remove(member)
            farewell.assert_awaited_once()

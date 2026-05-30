from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.feedback import FeedbackModal, feedback
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


@patch("commands.utility.feedback.feedbackIsBlocked", new_callable=AsyncMock, return_value=True)
async def test_feedback_blocked(mock_blocked, admin_command_info):
    ctx = MagicMock()
    await feedback(admin_command_info, ctx)
    admin_command_info.reply.assert_awaited_once()
    ctx.response.send_modal.assert_not_called()


@patch("commands.utility.feedback.feedbackIsBlocked", new_callable=AsyncMock, return_value=False)
async def test_feedback_opens_modal(mock_blocked, admin_command_info):
    ctx = MagicMock()
    ctx.response.send_modal = AsyncMock()
    await feedback(admin_command_info, ctx)
    ctx.response.send_modal.assert_awaited_once()


async def test_feedback_modal_unauthorized(admin_command_info):
    modal = FeedbackModal(admin_command_info, "t", "d")
    interaction = make_view_interaction(user=MagicMock(id=999))
    ok = await modal.interaction_check(interaction)
    assert ok is False


async def test_feedback_modal_submit(admin_command_info):
    modal = FeedbackModal(admin_command_info, "t", "d")
    channel = MagicMock()
    channel.send = AsyncMock()
    admin_command_info.client.get_channel = MagicMock(return_value=channel)
    modal.children = [MagicMock(value="Title here"), MagicMock(value="Description here enough")]
    interaction = make_view_interaction(admin_command_info.user)
    with patch("commands.utility.feedback.isinstance", return_value=True):
        await modal.on_submit(interaction)
    channel.send.assert_awaited_once()
    interaction.response.send_message.assert_awaited_once()


async def test_feedback_modal_submit_no_channel(admin_command_info):
    modal = FeedbackModal(admin_command_info, "t", "d")
    admin_command_info.client.get_channel = MagicMock(return_value=None)
    modal.children = [MagicMock(value="Title here"), MagicMock(value="Description here enough")]
    interaction = make_view_interaction(admin_command_info.user)
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_not_called()

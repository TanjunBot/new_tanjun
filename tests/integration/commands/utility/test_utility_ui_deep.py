from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.avatar import avatar
from commands.utility.feedback import feedback
from tests.helpers.view_state import embed_from_reply

pytestmark = pytest.mark.asyncio


async def test_feedback_sends_modal(admin_command_info) -> None:
    interaction = MagicMock()
    interaction.response.send_modal = AsyncMock()
    await feedback(admin_command_info, interaction)
    interaction.response.send_modal.assert_awaited_once()


async def test_avatar_self_embed(admin_command_info) -> None:
    await avatar(admin_command_info, admin_command_info.user)
    embed_from_reply(admin_command_info)


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock, return_value=[])
async def test_listscheduled_empty_reply(mock_get, admin_command_info) -> None:
    from commands.utility.listscheduled import list_scheduled_messages

    await list_scheduled_messages(admin_command_info)
    admin_command_info.reply.assert_awaited_once()

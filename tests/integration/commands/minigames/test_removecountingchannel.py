"""Integration tests for commands.minigames.counting.removecountingchannel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.minigames.counting.removecountingchannel import removeCountingChannel as command_fn


@pytest.mark.asyncio
@patch("commands.minigames.counting.removecountingchannel.require_counting_channel", new_callable=AsyncMock)
@patch("commands.minigames.counting.removecountingchannel.require_moderate_members", new_callable=AsyncMock)
async def test_not_configured(mock_mod, mock_req):
    mock_mod.return_value = False
    mock_req.return_value = None
    info = make_command_info()
    channel = make_text_channel()
    await command_fn(info, channel)
    info.reply.assert_not_awaited()

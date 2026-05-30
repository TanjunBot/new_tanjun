"""Integration tests for commands.utility.messagetrackingoptout."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.utility.messagetrackingoptout import optOut as command_fn


@pytest.mark.asyncio
@patch("commands.utility.messagetrackingoptout.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.messagetrackingoptout.opt_out", new_callable=AsyncMock)
async def test_optout_success(mock_out, mock_check):
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)
    mock_out.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.messagetrackingoptout.check_if_opted_out", new_callable=AsyncMock, return_value=True)
async def test_optout_already(mock_check):
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)

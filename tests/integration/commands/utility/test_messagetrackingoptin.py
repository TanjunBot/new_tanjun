"""Integration tests for commands.utility.messagetrackingoptin."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.utility.messagetrackingoptin import optIn as command_fn


@pytest.mark.asyncio
@patch("commands.utility.messagetrackingoptin.check_if_opted_out", new_callable=AsyncMock, return_value=True)
@patch("commands.utility.messagetrackingoptin.opt_in", new_callable=AsyncMock)
async def test_optin_success(mock_opt_in, mock_check):
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)
    mock_opt_in.assert_awaited_once()


@pytest.mark.asyncio
@patch("commands.utility.messagetrackingoptin.check_if_opted_out", new_callable=AsyncMock, return_value=False)
async def test_optin_already(mock_check):
    info = make_command_info()
    await command_fn(info)
    embed_from_reply(info.reply)

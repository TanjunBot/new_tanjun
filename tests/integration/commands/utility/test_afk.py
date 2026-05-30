"""Integration tests for commands.utility.afk."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.utility.afk import afk as command_fn


@pytest.mark.asyncio
@patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.afk.afk_service")
async def test_afk_set(mock_svc, mock_opt):
    mock_svc.is_afk = AsyncMock(return_value=False)
    mock_svc.set_afk = AsyncMock()
    info = make_command_info()
    await command_fn(info, "sleeping")
    embed_from_reply(info.reply)


@pytest.mark.asyncio
@patch("commands.utility.afk.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.utility.afk.afk_service")
async def test_afk_already(mock_svc, mock_opt):
    mock_svc.is_afk = AsyncMock(return_value=True)
    info = make_command_info()
    await command_fn(info, "sleeping")
    embed_from_reply(info.reply)

"""Integration tests for commands.logs.configure_logs."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.logs.configure_logs import configure_logs as command_fn


@pytest.mark.asyncio
async def test_missing_permission():
    user = make_member(guild_permissions=make_permissions(administrator=False))
    info = make_command_info(user=user)
    await command_fn(info)
    embed_from_reply(info.reply)

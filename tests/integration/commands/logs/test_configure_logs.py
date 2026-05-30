"""Integration tests for commands.logs.configure_logs."""

from __future__ import annotations

import pytest

from commands.logs.configure_logs import configure_logs as command_fn
from tests.helpers.discord import make_command_info, make_member, make_permissions
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_missing_permission():
    user = make_member(guild_permissions=make_permissions(administrator=False))
    info = make_command_info(user=user)
    await command_fn(info)
    embed_from_reply(info.reply)

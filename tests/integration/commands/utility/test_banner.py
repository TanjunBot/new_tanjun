"""Integration tests for commands.utility.banner."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.utility.banner import banner as command_fn


@pytest.mark.asyncio
async def test_banner_no_banner():
    target = make_member()
    fetched = make_member()
    fetched.banner = None
    fetched.display_name = "User"
    info = make_command_info()
    info.client.fetch_user = AsyncMock(return_value=fetched)
    await command_fn(info, target)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_banner_success():
    target = make_member()
    fetched = make_member()
    fetched.banner = MagicMock(url="https://cdn.discordapp.com/banner.png")
    fetched.display_name = "User"
    info = make_command_info()
    info.client.fetch_user = AsyncMock(return_value=fetched)
    await command_fn(info, target)
    embed_from_reply(info.reply)

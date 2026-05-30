"""Integration tests for commands.utility.avatar."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.utility.avatar import avatar as command_fn


@pytest.mark.asyncio
async def test_avatar_success():
    target = make_member(name="Target")
    target.display_name = "Target"
    target.display_avatar = MagicMock(url="https://cdn.discordapp.com/avatars/1.png")
    target.guild_avatar = None
    target.avatar = None
    info = make_command_info()
    await command_fn(info, target)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_avatar_with_guild_avatar():
    target = make_member()
    target.display_avatar = MagicMock(url="https://cdn.discordapp.com/a.png")
    target.guild_avatar = MagicMock()
    target.avatar = MagicMock(url="https://cdn.discordapp.com/b.png")
    info = make_command_info()
    await command_fn(info, target)
    embed_from_reply(info.reply)

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from commands.utility.avatar_decoration import avatarDecoration
from tests.helpers.discord import make_member


pytestmark = pytest.mark.asyncio


async def test_avatar_decoration_none(admin_command_info):
    user = make_member()
    user.avatar_decoration = None
    await avatarDecoration(admin_command_info, user)
    admin_command_info.reply.assert_awaited_once()


async def test_avatar_decoration_with_url(admin_command_info):
    user = make_member()
    user.avatar_decoration = MagicMock(url="https://cdn.example/dec.png")
    await avatarDecoration(admin_command_info, user)
    admin_command_info.reply.assert_awaited_once()

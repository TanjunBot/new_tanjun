"""Integration tests for commands.math.faculty."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.math.faculty import faculty_command as command_fn


@pytest.mark.asyncio
async def test_faculty_success():
    info = make_command_info()
    await command_fn(info, 5)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_faculty_zero():
    info = make_command_info()
    await command_fn(info, 0)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_faculty_negative():
    info = make_command_info()
    await command_fn(info, -1)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_faculty_too_large():
    info = make_command_info()
    await command_fn(info, 101)
    embed_from_reply(info.reply)

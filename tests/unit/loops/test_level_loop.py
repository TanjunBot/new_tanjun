from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from loops import level as level_loop
from tests.helpers.discord import make_guild, make_member

pytestmark = pytest.mark.asyncio


def test_get_member_no_guild():
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    assert level_loop._get_member(client, 1, 2) is None


def test_get_member_found():
    client = MagicMock()
    guild = make_guild()
    member = make_member()
    guild.get_member = MagicMock(return_value=member)
    client.get_guild = MagicMock(return_value=guild)
    assert level_loop._get_member(client, member.id, guild.id) is member


@pytest.mark.asyncio
async def test_fetch_xp_details():
    user = make_member()
    user.voice = MagicMock()
    user.voice.channel = MagicMock(id=999)
    with patch("loops.level.calculate_xp", new_callable=AsyncMock, return_value=10):
        xp = await level_loop.fetch_xp_details(user)
    assert xp == 10


@pytest.mark.asyncio
async def test_add_xp_skips_missing_member():
    client = MagicMock()
    client.get_guild = MagicMock(return_value=None)
    with patch("loops.level.voice_user_manager.get_active_users", return_value=[(1, 2)]):
        await level_loop.addXpToVoiceUsers(client)


@pytest.mark.asyncio
async def test_add_xp_skips_disabled_level_system():
    user = make_member()
    user.voice = MagicMock()
    user.voice.channel = MagicMock(id=1)
    guild = make_guild()
    guild.get_member = MagicMock(return_value=user)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    with (
        patch("loops.level.voice_user_manager.get_active_users", return_value=[(user.id, guild.id)]),
        patch("loops.level.get_level_system_status", new_callable=AsyncMock, return_value=False),
    ):
        await level_loop.addXpToVoiceUsers(client)


@pytest.mark.asyncio
async def test_add_xp_skips_blacklisted():
    user = make_member()
    user.voice = MagicMock()
    user.voice.channel = MagicMock(id=1)
    guild = make_guild()
    guild.get_member = MagicMock(return_value=user)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    with (
        patch("loops.level.voice_user_manager.get_active_users", return_value=[(user.id, guild.id)]),
        patch("loops.level.get_level_system_status", new_callable=AsyncMock, return_value=True),
        patch("loops.level.is_entity_blacklisted", new_callable=AsyncMock, return_value=True),
    ):
        await level_loop.addXpToVoiceUsers(client)


@pytest.mark.asyncio
async def test_add_xp_updates_user():
    user = make_member()
    user.voice = MagicMock()
    user.voice.channel = MagicMock(id=1)
    guild = make_guild()
    guild.get_member = MagicMock(return_value=user)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    with (
        patch("loops.level.voice_user_manager.get_active_users", return_value=[(user.id, guild.id)]),
        patch("loops.level.get_level_system_status", new_callable=AsyncMock, return_value=True),
        patch("loops.level.is_entity_blacklisted", new_callable=AsyncMock, return_value=False),
        patch("loops.level.fetch_xp_details", new_callable=AsyncMock, return_value=5),
        patch("loops.level.update_user_xp_from_voice", new_callable=AsyncMock) as mock_update,
    ):
        await level_loop.addXpToVoiceUsers(client)
    mock_update.assert_awaited_once()

"""Unit tests for message XP minigame handler."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from minigames.add_level_xp import addLevelXp, fetch_xp_details
from tests.helpers.discord import make_guild, make_member, make_message


@pytest.mark.unit
class TestAddLevelXp:
    @pytest.mark.asyncio
    async def test_opted_out_user_skipped(self):
        message = make_message()
        with patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=True):
            with patch("minigames.add_level_xp.get_level_system_status", new_callable=AsyncMock) as level_status:
                await addLevelXp(message)
                level_status.assert_not_called()

    @pytest.mark.asyncio
    async def test_dm_message_skipped(self):
        message = make_message()
        message.guild = None
        with (
            patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames.add_level_xp.get_level_system_status", new_callable=AsyncMock) as level_status,
        ):
            await addLevelXp(message)
            level_status.assert_not_called()

    @pytest.mark.asyncio
    async def test_level_system_disabled_skipped(self):
        guild = make_guild()
        message = make_message(guild=guild)
        with (
            patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames.add_level_xp.get_level_system_status", new_callable=AsyncMock, return_value=False),
            patch("minigames.add_level_xp.update_user_xp", new_callable=AsyncMock) as update_xp,
        ):
            await addLevelXp(message)
            update_xp.assert_not_called()

    @pytest.mark.asyncio
    async def test_blacklisted_entity_skipped(self):
        author = make_member()
        author.roles = []
        guild = make_guild()
        message = make_message(author=author, guild=guild)
        with (
            patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=False),
            patch("minigames.add_level_xp.get_level_system_status", new_callable=AsyncMock, return_value=True),
            patch("minigames.add_level_xp.is_entity_blacklisted", new_callable=AsyncMock, return_value=True),
            patch("minigames.add_level_xp.update_user_xp", new_callable=AsyncMock) as update_xp,
        ):
            await addLevelXp(message)
            update_xp.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_xp_details_gathers_config(self):
        message = make_message()
        message.author.roles = []
        with (
            patch("minigames.add_level_xp._get_cached_config", new_callable=AsyncMock, return_value="medium"),
            patch("minigames.add_level_xp.calculate_xp", new_callable=AsyncMock, return_value=3),
        ):
            scaling, formula, xp = await fetch_xp_details(message, "123")
        assert scaling == "medium"
        assert xp == 3

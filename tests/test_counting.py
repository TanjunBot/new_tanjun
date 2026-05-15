"""Tests for minigames/counting.py and countingChallenge.py — comprehensive."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tests.mock_config import patch_config_module

patch_config_module()


class TestCountingModuleImport:
    def test_counting_function_exists(self):
        from minigames.counting import counting
        assert callable(counting)


class TestCountingChallengeModuleImport:
    def test_challenge_function_exists(self):
        from minigames.countingChallenge import counting
        assert callable(counting)


class TestWordchainModuleImport:
    def test_wordchain_function_exists(self):
        from minigames.wordchain import wordchain
        assert callable(wordchain)


class TestAddLevelXpModuleImport:
    def test_addLevelXp_function_exists(self):
        from minigames.addLevelXp import addLevelXp
        assert callable(addLevelXp)

    def test_clearNotifiedUsers_function_exists(self):
        from minigames.addLevelXp import clearNotifiedUsers
        assert callable(clearNotifiedUsers)

    def test_calculate_xp_function_exists(self):
        from minigames.addLevelXp import calculate_xp
        assert callable(calculate_xp)

    def test_is_blacklisted_function_exists(self):
        from minigames.addLevelXp import is_blacklisted
        assert callable(is_blacklisted)

    def test_fetch_xp_details_function_exists(self):
        from minigames.addLevelXp import fetch_xp_details
        assert callable(fetch_xp_details)

    def test_handle_level_up_function_exists(self):
        from minigames.addLevelXp import handle_level_up
        assert callable(handle_level_up)

    def test_notifiedUsers_is_list(self):
        from minigames.addLevelXp import notifiedUsers
        assert isinstance(notifiedUsers, list)


class TestAddLevelXpClearNotifiedUsers:
    def test_clear_resets_list(self):
        from minigames.addLevelXp import clearNotifiedUsers, notifiedUsers
        notifiedUsers.append(12345)
        assert 12345 in notifiedUsers
        clearNotifiedUsers()
        from minigames.addLevelXp import notifiedUsers as fresh
        # After clear, list should be empty
        assert len(fresh) == 0

    def test_clear_on_empty_list(self):
        from minigames.addLevelXp import clearNotifiedUsers
        clearNotifiedUsers()  # Should not raise

    def test_clear_multiple_times(self):
        from minigames.addLevelXp import clearNotifiedUsers
        clearNotifiedUsers()
        clearNotifiedUsers()
        clearNotifiedUsers()  # Should not raise


class TestAddLevelXpCalculateXp:
    """Test calculate_xp with mocked Discord objects."""

    @pytest.mark.asyncio
    async def test_calculate_xp_returns_int(self):
        from minigames.addLevelXp import calculate_xp
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.author.id = 12345
        mock_message.author.roles = []
        mock_message.channel = MagicMock()
        mock_message.channel.id = "99999"
        mock_message.guild = MagicMock()
        mock_message.guild.id = "88888"

        with patch("minigames.addLevelXp.get_user_boost", new_callable=AsyncMock, return_value=None), \
             patch("minigames.addLevelXp.get_user_roles_boosts", new_callable=AsyncMock, return_value=[]), \
             patch("minigames.addLevelXp.get_channel_boost", new_callable=AsyncMock, return_value=None):
            result = await calculate_xp(mock_message, "88888")
            assert isinstance(result, int)
            assert 1 <= result <= 3  # base_xp is randint(1,3) with no boosts

    @pytest.mark.asyncio
    async def test_calculate_xp_with_additive_user_boost(self):
        from minigames.addLevelXp import calculate_xp
        from models import XpBoostModel
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.author.id = 12345
        mock_message.author.roles = []
        mock_message.channel = MagicMock()
        mock_message.channel.id = "99999"
        mock_message.guild = MagicMock()
        mock_message.guild.id = "88888"

        boost = XpBoostModel(boost=2.0, additive=True)
        with patch("minigames.addLevelXp.get_user_boost", new_callable=AsyncMock, return_value=boost), \
             patch("minigames.addLevelXp.get_user_roles_boosts", new_callable=AsyncMock, return_value=[]), \
             patch("minigames.addLevelXp.get_channel_boost", new_callable=AsyncMock, return_value=None):
            result = await calculate_xp(mock_message, "88888")
            # additive boost of 2.0 adds 1.0 to additive total (2.0 - 1.0 = 1.0)
            # total_boost = (1 + 1.0) * 1.0 = 2.0
            # result = base_xp * 2, so result is 2, 4, or 6
            assert result in [2, 4, 6]

    @pytest.mark.asyncio
    async def test_calculate_xp_with_multiplicative_user_boost(self):
        from minigames.addLevelXp import calculate_xp
        from models import XpBoostModel
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.author.id = 12345
        mock_message.author.roles = []
        mock_message.channel = MagicMock()
        mock_message.channel.id = "99999"
        mock_message.guild = MagicMock()
        mock_message.guild.id = "88888"

        boost = XpBoostModel(boost=2.0, additive=False)
        with patch("minigames.addLevelXp.get_user_boost", new_callable=AsyncMock, return_value=boost), \
             patch("minigames.addLevelXp.get_user_roles_boosts", new_callable=AsyncMock, return_value=[]), \
             patch("minigames.addLevelXp.get_channel_boost", new_callable=AsyncMock, return_value=None):
            result = await calculate_xp(mock_message, "88888")
            # multiplicative boost of 2.0 multiplies total by 2.0
            # result = base_xp * 2, so result is 2, 4, or 6
            assert result in [2, 4, 6]


class TestAddLevelXpIsBlacklisted:
    @pytest.mark.asyncio
    async def test_not_blacklisted(self):
        from minigames.addLevelXp import is_blacklisted
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.author.id = 12345
        mock_message.channel = MagicMock()
        mock_message.channel.id = 67890
        mock_message.author.roles = []

        with patch("minigames.addLevelXp.get_blacklist", new_callable=AsyncMock, return_value={"channels": [], "roles": [], "users": []}):
            result = await is_blacklisted(mock_message, "guild1")
            assert result is False

    @pytest.mark.asyncio
    async def test_blacklisted_user(self):
        from minigames.addLevelXp import is_blacklisted
        from models import BlacklistEntryModel
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.author.id = 12345
        mock_message.channel = MagicMock()
        mock_message.channel.id = 67890
        mock_message.author.roles = []

        blacklist = {"channels": [], "roles": [], "users": [BlacklistEntryModel(entity_id="12345", reason="spam")]}
        with patch("minigames.addLevelXp.get_blacklist", new_callable=AsyncMock, return_value=blacklist):
            result = await is_blacklisted(mock_message, "guild1")
            assert result is True

    @pytest.mark.asyncio
    async def test_blacklisted_channel(self):
        from minigames.addLevelXp import is_blacklisted
        from models import BlacklistEntryModel
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.author.id = 12345
        mock_message.channel = MagicMock()
        mock_message.channel.id = 67890
        mock_message.author.roles = []

        blacklist = {"channels": [BlacklistEntryModel(entity_id="67890", reason=None)], "roles": [], "users": []}
        with patch("minigames.addLevelXp.get_blacklist", new_callable=AsyncMock, return_value=blacklist):
            result = await is_blacklisted(mock_message, "guild1")
            assert result is True

    @pytest.mark.asyncio
    async def test_blacklisted_role(self):
        from minigames.addLevelXp import is_blacklisted
        from models import BlacklistEntryModel
        mock_role = MagicMock()
        mock_role.id = 55555
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.author.id = 12345
        mock_message.author.roles = [mock_role]
        mock_message.channel = MagicMock()
        mock_message.channel.id = 67890

        blacklist = {"channels": [], "roles": [BlacklistEntryModel(entity_id="55555", reason=None)], "users": []}
        with patch("minigames.addLevelXp.get_blacklist", new_callable=AsyncMock, return_value=blacklist):
            result = await is_blacklisted(mock_message, "guild1")
            assert result is True
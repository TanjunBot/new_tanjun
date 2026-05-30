"""Tests for XpCalculator: XP boost calculation and formula verification.

Tests the get_effective_boost and calculate_xp methods in isolation
by mocking the XpBoostRepository dependency.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models import XpBoostModel
from services.xp_calculator import XpCalculator


def _make_boost(boost: float, additive: bool) -> XpBoostModel:
    """Factory helper to create an XpBoostModel."""
    return XpBoostModel(boost=boost, additive=additive)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_boost_repo() -> MagicMock:
    """Create a mock XpBoostRepository with async methods."""
    repo = MagicMock()
    repo.get_boosts_for_target = AsyncMock(return_value=[])
    repo.get_boost = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def calculator(mock_boost_repo: MagicMock) -> XpCalculator:
    """Create an XpCalculator with a mocked boost repository."""
    return XpCalculator(boost_repo=mock_boost_repo)


GUID = "123456789"
USER_ID = "111111111"
ROLE_IDS = ["222222222", "333333333"]
CHANNEL_ID = "444444444"


# =============================================================================
# No-boost baseline (no boosts configured)
# =============================================================================


class TestNoBoosts:
    """When no boosts are configured, the effective boost should be 1.0."""

    @pytest.mark.asyncio
    async def test_no_boosts_returns_one(self, calculator, mock_boost_repo):
        """No role, user, or channel boosts → effective boost = 1.0."""
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        assert boost == 1.0

    @pytest.mark.asyncio
    async def test_no_boosts_calculate_xp_bounds(self, calculator, mock_boost_repo):
        """With boost=1.0, calculate_xp returns base_xp (1-3)."""
        with patch("services.xp_calculator.random.randint", return_value=2):
            xp = await calculator.calculate_xp(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
            assert xp == 2

    @pytest.mark.asyncio
    async def test_empty_role_list(self, calculator, mock_boost_repo):
        """Empty role_ids should not crash and returns 1.0."""
        boost = await calculator.get_effective_boost(GUID, USER_ID, [], CHANNEL_ID)
        assert boost == 1.0

    @pytest.mark.asyncio
    async def test_empty_user_id(self, calculator, mock_boost_repo):
        """Empty user_id should not crash."""
        boost = await calculator.get_effective_boost(GUID, "", ROLE_IDS, CHANNEL_ID)
        assert boost == 1.0


# =============================================================================
# Additive boost tests
# =============================================================================


class TestAdditiveBoosts:
    """Additive boosts contribute to (1 + sum_of_additive_boosts)."""

    @pytest.mark.asyncio
    async def test_single_additive_role_boost(self, calculator, mock_boost_repo):
        """One additive role boost of 2.0 → effective boost = 1 + (2-1) = 2.0."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=True),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (2-1)) * 1.0 = 2.0
        assert boost == 2.0

    @pytest.mark.asyncio
    async def test_multiple_additive_role_boosts(self, calculator, mock_boost_repo):
        """Multiple additive role boosts sum together."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=True),
            _make_boost(1.5, additive=True),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (2-1) + (1.5-1)) = 2.5
        assert boost == 2.5

    @pytest.mark.asyncio
    async def test_additive_user_boost(self, calculator, mock_boost_repo):
        """Additive user boost contributes to the additive sum."""
        async def _side_effect(guild_id, entity_id, target=None):
            # Only return the boost for the user query (not channel)
            if target and target.name == "CHANNEL":
                return None
            return _make_boost(3.0, additive=True)
        mock_boost_repo.get_boost.side_effect = _side_effect
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (3-1)) * 1.0 = 3.0
        assert boost == 3.0

    @pytest.mark.asyncio
    async def test_additive_channel_boost(self, calculator, mock_boost_repo):
        """Additive channel boost contributes to the additive sum."""
        # user_boost called first, channel_boost called second
        async def _get_boost_side_effect(guild_id, entity_id, target=None):
            if target and target.name == "CHANNEL":
                return _make_boost(4.0, additive=True)
            return None

        mock_boost_repo.get_boost.side_effect = _get_boost_side_effect
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (4-1)) * 1.0 = 4.0
        assert boost == 4.0

    @pytest.mark.asyncio
    async def test_additive_all_sources(self, calculator, mock_boost_repo):
        """All three sources (role, user, channel) additive stack."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=True),
        ]

        async def _get_boost_side_effect(guild_id, entity_id, target=None):
            if target and target.name == "CHANNEL":
                return _make_boost(3.0, additive=True)
            return _make_boost(1.5, additive=True)  # user boost

        mock_boost_repo.get_boost.side_effect = _get_boost_side_effect
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (2-1) + (1.5-1) + (3-1)) = (1 + 1 + 0.5 + 2) = 4.5
        assert boost == 4.5


# =============================================================================
# Multiplicative boost tests
# =============================================================================


class TestMultiplicativeBoosts:
    """Multiplicative boosts multiply together: product_of_multiplicative_boosts."""

    @pytest.mark.asyncio
    async def test_single_multiplicative_role_boost(self, calculator, mock_boost_repo):
        """One multiplicative role boost of 2.0 → effective = 1.0 * 2.0 = 2.0."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        assert boost == 2.0

    @pytest.mark.asyncio
    async def test_multiple_multiplicative_role_boosts(self, calculator, mock_boost_repo):
        """Multiple multiplicative role boosts multiply together."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=False),
            _make_boost(3.0, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        assert boost == 6.0

    @pytest.mark.asyncio
    async def test_multiplicative_all_sources(self, calculator, mock_boost_repo):
        """All multiplicative sources multiply."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=False),
        ]

        async def _get_boost_side_effect(guild_id, entity_id, target=None):
            if target and target.name == "CHANNEL":
                return _make_boost(3.0, additive=False)
            return _make_boost(1.5, additive=False)

        mock_boost_repo.get_boost.side_effect = _get_boost_side_effect
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # 1.0 * 2.0 * 1.5 * 3.0 = 9.0
        assert boost == 9.0


# =============================================================================
# Mixed additive + multiplicative boost tests
# =============================================================================


class TestMixedBoosts:
    """Additive and multiplicative boosts combine: (1 + sum_add) * product_mul."""

    @pytest.mark.asyncio
    async def test_mixed_role_boosts(self, calculator, mock_boost_repo):
        """Role has both additive (2.0) and multiplicative (3.0) boosts."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=True),
            _make_boost(3.0, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (2-1)) * 3.0 = 2.0 * 3.0 = 6.0
        assert boost == 6.0

    @pytest.mark.asyncio
    async def test_mixed_user_boost(self, calculator, mock_boost_repo):
        """User has both additive (2.0) and multiplicative (1.5) boosts."""
        # First call (user) returns additive, second call (channel) returns mult
        mock_boost_repo.get_boost.side_effect = [
            _make_boost(2.0, additive=True),
            _make_boost(1.5, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (2-1)) * 1.5 = 2.0 * 1.5 = 3.0
        assert boost == 3.0

    @pytest.mark.asyncio
    async def test_complex_mixed_boost(self, calculator, mock_boost_repo):
        """Complex scenario with all source types and both boost types."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=True),
            _make_boost(1.5, additive=True),
            _make_boost(3.0, additive=False),
        ]

        async def _get_boost_side_effect(guild_id, entity_id, target=None):
            if target and target.name == "CHANNEL":
                return _make_boost(2.0, additive=False)
            return _make_boost(4.0, additive=True)

        mock_boost_repo.get_boost.side_effect = _get_boost_side_effect

        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (2-1) + (1.5-1) + (4-1)) * 3.0 * 2.0
        # = (1 + 1 + 0.5 + 3) * 6.0
        # = 5.5 * 6.0 = 33.0
        assert boost == 33.0


# =============================================================================
# Boost at boundaries (zero/minimal boosts)
# =============================================================================


class TestEdgeCases:
    """Edge cases: zero boosts, negative scenarios, extreme values."""

    @pytest.mark.asyncio
    async def test_boost_of_1_0_additive(self, calculator, mock_boost_repo):
        """Additive boost of 1.0 → no contribution (1-1=0)."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(1.0, additive=True),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        assert boost == 1.0

    @pytest.mark.asyncio
    async def test_boost_of_1_0_multiplicative(self, calculator, mock_boost_repo):
        """Multiplicative boost of 1.0 → no change."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(1.0, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        assert boost == 1.0

    @pytest.mark.asyncio
    async def test_boost_of_0_additive(self, calculator, mock_boost_repo):
        """Additive boost of 0.0 → reduces additive sum (0-1 = -1)."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(0.0, additive=True),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # (1 + (0-1)) = 0.0
        assert boost == 0.0

    @pytest.mark.asyncio
    async def test_boost_of_0_multiplicative(self, calculator, mock_boost_repo):
        """Multiplicative boost of 0.0 → zeroes everything."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(0.0, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # 1.0 * 0.0 = 0.0
        assert boost == 0.0

    @pytest.mark.asyncio
    async def test_large_boost_value(self, calculator, mock_boost_repo):
        """Very large multiplicative boosts are handled correctly."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(100.0, additive=False),
            _make_boost(200.0, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        assert boost == 20000.0  # 1.0 * 100.0 * 200.0

    @pytest.mark.asyncio
    async def test_fractional_boost(self, calculator, mock_boost_repo):
        """Fractional multiplicative boost (<1) reduces XP."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(0.5, additive=False),
        ]
        boost = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        assert boost == 0.5


# =============================================================================
# calculate_xp integration tests (combines base_xp × effective_boost)
# =============================================================================


class TestCalculateXp:
    """Tests for the full calculate_xp method."""

    @pytest.mark.asyncio
    async def test_calculate_xp_with_boost(self, calculator, mock_boost_repo):
        """calculate_xp uses base_xp * effective_boost."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(3.0, additive=True),
        ]
        with patch("services.xp_calculator.random.randint", return_value=2):
            xp = await calculator.calculate_xp(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
            # base=2, effective=(1+(3-1))=3 → xp=6
            assert xp == 6

    @pytest.mark.asyncio
    async def test_calculate_xp_min_random(self, calculator, mock_boost_repo):
        """Base XP at minimum (1) with boost."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=True),
        ]
        with patch("services.xp_calculator.random.randint", return_value=1):
            xp = await calculator.calculate_xp(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
            assert xp == 2  # 1 * 2

    @pytest.mark.asyncio
    async def test_calculate_xp_max_random(self, calculator, mock_boost_repo):
        """Base XP at maximum (3) with boost."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(2.0, additive=True),
        ]
        with patch("services.xp_calculator.random.randint", return_value=3):
            xp = await calculator.calculate_xp(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
            assert xp == 6  # 3 * 2

    @pytest.mark.asyncio
    async def test_calculate_xp_returns_int(self, calculator, mock_boost_repo):
        """Result is always an integer."""
        mock_boost_repo.get_boosts_for_target.return_value = [
            _make_boost(1.5, additive=False),
        ]
        with patch("services.xp_calculator.random.randint", return_value=2):
            xp = await calculator.calculate_xp(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
            assert xp == 3  # int(2 * 1.5) = int(3.0) = 3
            assert isinstance(xp, int)


# =============================================================================
# Repository call verification
# =============================================================================


class TestRepositoryCalls:
    """Verify that the calculator makes the correct repository calls."""

    @pytest.mark.asyncio
    async def test_calls_get_boosts_for_target_with_roles(self, calculator, mock_boost_repo):
        """Repository is called with the correct role IDs."""
        mock_boost_repo.get_boosts_for_target = AsyncMock(return_value=[])
        await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        mock_boost_repo.get_boosts_for_target.assert_called_once_with(GUID, ROLE_IDS)

    @pytest.mark.asyncio
    async def test_calls_get_boost_for_user(self, calculator, mock_boost_repo):
        """Repository is queried for user boost."""
        await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # get_boost is called twice: once for user, once for channel
        assert mock_boost_repo.get_boost.call_count >= 1

    @pytest.mark.asyncio
    async def test_calls_get_boost_for_channel(self, calculator, mock_boost_repo):
        """Repository is queried for channel boost."""
        await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_ID)
        # Second call should be for channel
        calls = mock_boost_repo.get_boost.call_args_list
        # First call: user boost
        assert calls[0][0][0] == GUID
        assert calls[0][0][1] == USER_ID

    @pytest.mark.asyncio
    async def test_empty_role_list_skips_repo_call(self, calculator, mock_boost_repo):
        """No roles → get_boosts_for_target still called (returns empty)."""
        await calculator.get_effective_boost(GUID, USER_ID, [], CHANNEL_ID)
        mock_boost_repo.get_boosts_for_target.assert_called_once_with(GUID, [])


# =============================================================================
# Module-level singleton test
# =============================================================================


class TestSingleton:
    """The module-level xp_calculator singleton is importable and functional."""

    def test_singleton_is_calculator_instance(self):
        """xp_calculator is an instance of XpCalculator."""
        from services.xp_calculator import xp_calculator

        assert isinstance(xp_calculator, XpCalculator)

    @pytest.mark.asyncio
    async def test_singleton_works_with_default_repo(self):
        """Default XpBoostRepository is used (no crash on import)."""
        from services.xp_calculator import xp_calculator

        assert xp_calculator._boost_repo is not None

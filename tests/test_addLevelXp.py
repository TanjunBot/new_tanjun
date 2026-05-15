"""Tests for addLevelXp helper functions — comprehensive."""

import math

import pytest

from tests.mock_config import patch_config_module

patch_config_module()


class TestXpBoostModelIntegration:
    """Test that XpBoostModel works correctly with the XP calculation system."""

    def test_additive_boost_model(self):
        from models import XpBoostModel

        boost = XpBoostModel(boost=2.0, additive=True)
        assert boost.boost == 2.0
        assert boost.additive is True

    def test_multiplicative_boost_model(self):
        from models import XpBoostModel

        boost = XpBoostModel(boost=1.5, additive=False)
        assert boost.boost == 1.5
        assert boost.additive is False

    def test_boost_model_zero(self):
        from models import XpBoostModel

        boost = XpBoostModel(boost=0.0, additive=True)
        assert boost.boost == 0.0


class TestBlacklistEntryModelIntegration:
    """Test BlacklistEntryModel as used by is_blacklisted."""

    def test_blacklist_entry_with_reason(self):
        from models import BlacklistEntryModel

        entry = BlacklistEntryModel(entity_id="12345", reason="spam")
        assert entry.entity_id == "12345"
        assert entry.reason == "spam"

    def test_blacklist_entry_without_reason(self):
        from models import BlacklistEntryModel

        entry = BlacklistEntryModel(entity_id="12345", reason=None)
        assert entry.entity_id == "12345"
        assert entry.reason is None

    def test_blacklist_entry_default_reason(self):
        from models import BlacklistEntryModel

        entry = BlacklistEntryModel(entity_id="12345")
        assert entry.reason is None


class TestLevelSystemStatus:
    """Test get_level_system_status behavior with mocked DB."""

    @pytest.mark.asyncio
    async def test_level_system_status_no_pool_returns_true(self):
        """When pool is None, get_level_system_status should return True (default)."""
        import api

        api._bot = None
        result = await api.get_level_system_status("guild1")
        assert result is True

    @pytest.mark.asyncio
    async def test_get_xp_scaling_no_pool(self):
        import api

        api._bot = None
        result = await api.get_xp_scaling("guild1")
        assert result == "medium"  # Default


class TestMathImports:
    """Verify math functions used in XP calculations work correctly."""

    def test_prod_empty_iterable(self):
        assert math.prod([]) == 1  # identity for multiplication

    def test_prod_single_element(self):
        assert math.prod([5]) == 5

    def test_prod_multiple_elements(self):
        assert math.prod([2, 3, 4]) == 24

    def test_random_xp_base_range(self):
        """Base XP should be between 1 and 3."""
        import random

        for _ in range(100):
            xp = random.randint(1, 3)
            assert 1 <= xp <= 3


class TestXpScalingFunctions:
    """Test XP scaling formulas used by addLevelXp."""

    def test_easy_scaling(self):
        from utility import LEVEL_SCALINGS

        for level in [1, 5, 10, 50]:
            xp = LEVEL_SCALINGS["easy"](level)
            assert xp == 100 * level

    def test_medium_scaling(self):
        from utility import LEVEL_SCALINGS

        for level in [1, 5, 10]:
            xp = LEVEL_SCALINGS["medium"](level)
            assert xp == 100 * (level**1.5)

    def test_hard_scaling(self):
        from utility import LEVEL_SCALINGS

        for level in [1, 5, 10]:
            xp = LEVEL_SCALINGS["hard"](level)
            assert xp == 100 * (level**2)

    def test_extreme_scaling(self):
        from utility import LEVEL_SCALINGS

        for level in [1, 5, 10]:
            xp = LEVEL_SCALINGS["extreme"](level)
            assert xp == 100 * (level**2.5)

    def test_unknown_scaling_returns_medium(self):
        """get_xp_for_level with unknown scaling defaults to medium."""
        import math

        from utility import get_xp_for_level

        result = get_xp_for_level(5, "nonexistent")
        expected = math.floor(100 * (5**1.5))
        assert result == expected

    def test_custom_formula(self):
        """Custom formulas use eval_expr for XP calculation."""
        from utility import get_xp_for_level

        result = get_xp_for_level(5, "custom", custom_formula="100*5")
        assert result == 500

    def test_custom_formula_with_level_var(self):
        """Custom formulas with level variable use eval_expr for XP calculation."""
        from utility import get_xp_for_level

        result = get_xp_for_level(10, "custom", custom_formula="100*level")
        assert result == 1000

    def test_custom_formula_invalid_returns_zero(self):
        from utility import get_xp_for_level

        result = get_xp_for_level(5, "custom", custom_formula="invalid!!")
        assert result == 0

    def test_level_zero_returns_zero(self):
        from utility import get_xp_for_level

        assert get_xp_for_level(0, "easy") == 0

    def test_negative_level_returns_zero(self):
        from utility import get_xp_for_level

        assert get_xp_for_level(-1, "easy") == 0

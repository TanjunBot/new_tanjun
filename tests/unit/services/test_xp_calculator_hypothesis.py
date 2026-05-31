"""Hypothesis property tests for services/xp_calculator.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from api import BoostTarget
from models import XpBoostModel
from services.xp_calculator import XpCalculator

pytestmark = pytest.mark.unit


def _make_boost(boost: float, additive: bool) -> XpBoostModel:
    return XpBoostModel(boost=boost, additive=additive)


def _expected_boost(
    role_boosts: list[tuple[float, bool]],
    user_boost: tuple[float, bool] | None,
    channel_boost: tuple[float, bool] | None,
) -> float:
    total_additive = 0.0
    total_multiplicative = 1.0
    for boost, additive in role_boosts:
        if additive:
            total_additive += boost - 1
        else:
            total_multiplicative *= boost
    if user_boost:
        boost, additive = user_boost
        if additive:
            total_additive += boost - 1
        else:
            total_multiplicative *= boost
    if channel_boost:
        boost, additive = channel_boost
        if additive:
            total_additive += boost - 1
        else:
            total_multiplicative *= boost
    return (1.0 + total_additive) * total_multiplicative


def _make_repo(
    role_boosts: list[XpBoostModel],
    user_boost: XpBoostModel | None,
    channel_boost: XpBoostModel | None,
) -> MagicMock:
    repo = MagicMock()
    repo.get_boosts_for_target = AsyncMock(return_value=role_boosts)

    async def _get_boost(guild_id: str, entity_id: str, target=None) -> XpBoostModel | None:
        if target == BoostTarget.CHANNEL:
            return channel_boost
        return user_boost

    repo.get_boost = AsyncMock(side_effect=_get_boost)
    return repo


boost_pair = st.tuples(st.floats(min_value=1.0, max_value=20.0, allow_nan=False), st.booleans())
boost_list = st.lists(boost_pair, max_size=6)
optional_boost = st.one_of(st.none(), boost_pair)
base_xp = st.integers(min_value=1, max_value=3)

GUID = "12345678901234567"
USER_ID = "11111111111111111"
ROLE_IDS = ["22222222222222222", "33333333333333333"]
CHANNEL_A = "44444444444444444"
CHANNEL_B = "55555555555555555"


class TestEffectiveBoostHypothesis:
    @given(role_boosts=boost_list, user_boost=optional_boost, channel_boost=optional_boost)
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_formula_matches_manual(
        self,
        role_boosts: list[tuple[float, bool]],
        user_boost: tuple[float, bool] | None,
        channel_boost: tuple[float, bool] | None,
    ) -> None:
        role_models = [_make_boost(b, a) for b, a in role_boosts]
        user_model = _make_boost(*user_boost) if user_boost else None
        channel_model = _make_boost(*channel_boost) if channel_boost else None
        calculator = XpCalculator(boost_repo=_make_repo(role_models, user_model, channel_model))

        result = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_A)
        expected = _expected_boost(role_boosts, user_boost, channel_boost)
        assert result == pytest.approx(expected)

    @given(role_boosts=boost_list, user_boost=optional_boost, channel_boost=optional_boost)
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_result_at_least_one_with_non_negative_boosts(
        self,
        role_boosts: list[tuple[float, bool]],
        user_boost: tuple[float, bool] | None,
        channel_boost: tuple[float, bool] | None,
    ) -> None:
        role_models = [_make_boost(b, a) for b, a in role_boosts]
        user_model = _make_boost(*user_boost) if user_boost else None
        channel_model = _make_boost(*channel_boost) if channel_boost else None
        calculator = XpCalculator(boost_repo=_make_repo(role_models, user_model, channel_model))

        result = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_A)
        assert result >= 1.0

    @given(
        role_boosts=st.lists(
            st.tuples(st.floats(min_value=1.0, max_value=5.0, allow_nan=False), st.just(True)),
            min_size=1,
            max_size=5,
        )
    )
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_additive_role_boosts_stack(self, role_boosts: list[tuple[float, bool]]) -> None:
        role_models = [_make_boost(b, a) for b, a in role_boosts]
        calculator = XpCalculator(boost_repo=_make_repo(role_models, None, None))

        result = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_A)
        additive_sum = sum(b - 1 for b, _ in role_boosts)
        assert result == pytest.approx(1.0 + additive_sum)

    @given(channel_boost=boost_pair)
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_channel_boost_isolation(self, channel_boost: tuple[float, bool]) -> None:
        channel_model = _make_boost(*channel_boost)
        repo = MagicMock()
        repo.get_boosts_for_target = AsyncMock(return_value=[])
        repo.get_boost = AsyncMock(return_value=None)

        calculator_a = XpCalculator(boost_repo=repo)

        async def _get_boost_with_channel(guild_id: str, entity_id: str, target=None) -> XpBoostModel | None:
            if target == BoostTarget.CHANNEL and entity_id == CHANNEL_A:
                return channel_model
            return None

        repo.get_boost = AsyncMock(side_effect=_get_boost_with_channel)
        boost_a = await calculator_a.get_effective_boost(GUID, USER_ID, [], CHANNEL_A)

        repo.get_boost = AsyncMock(return_value=None)
        calculator_b = XpCalculator(boost_repo=repo)
        boost_b = await calculator_b.get_effective_boost(GUID, USER_ID, [], CHANNEL_B)

        assert boost_a == pytest.approx(_expected_boost([], None, channel_boost))
        assert boost_b == 1.0


class TestCalculateXpHypothesis:
    @given(
        role_boosts=boost_list,
        user_boost=optional_boost,
        channel_boost=optional_boost,
        base=base_xp,
    )
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_calculate_xp_returns_int_in_valid_range(
        self,
        role_boosts: list[tuple[float, bool]],
        user_boost: tuple[float, bool] | None,
        channel_boost: tuple[float, bool] | None,
        base: int,
    ) -> None:
        role_models = [_make_boost(b, a) for b, a in role_boosts]
        user_model = _make_boost(*user_boost) if user_boost else None
        channel_model = _make_boost(*channel_boost) if channel_boost else None
        calculator = XpCalculator(boost_repo=_make_repo(role_models, user_model, channel_model))
        effective = _expected_boost(role_boosts, user_boost, channel_boost)

        with patch("services.xp_calculator.random.randint", return_value=base):
            xp = await calculator.calculate_xp(GUID, USER_ID, ROLE_IDS, CHANNEL_A)

        assert isinstance(xp, int)
        assert xp == int(base * effective)
        assert xp >= int(base * 1.0)


class TestBoostEdgeCasesHypothesis:
    @given(channel_boost=boost_pair)
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_empty_role_boosts_with_channel_only(self, channel_boost: tuple[float, bool]) -> None:
        channel_model = _make_boost(*channel_boost)
        repo = _make_repo([], None, channel_model)
        calculator = XpCalculator(boost_repo=repo)
        result = await calculator.get_effective_boost(GUID, USER_ID, [], CHANNEL_A)
        assert result == pytest.approx(_expected_boost([], None, channel_boost))

    @given(user_boost=boost_pair)
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_multiplicative_user_only(self, user_boost: tuple[float, bool]) -> None:
        user_model = _make_boost(*user_boost)
        calculator = XpCalculator(boost_repo=_make_repo([], user_model, None))
        result = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_A)
        assert result == pytest.approx(_expected_boost([], user_boost, None))

    @given(user_boost=st.tuples(st.floats(min_value=1.0, max_value=5.0), st.just(True)))
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_additive_user_only(self, user_boost: tuple[float, bool]) -> None:
        user_model = _make_boost(*user_boost)
        calculator = XpCalculator(boost_repo=_make_repo([], user_model, None))
        result = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_A)
        assert result == pytest.approx(1.0 + (user_boost[0] - 1))

    @given(
        role_boosts=st.lists(
            st.tuples(st.floats(min_value=1.0, max_value=3.0), st.just(False)),
            min_size=1,
            max_size=4,
        )
    )
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_multiplicative_role_product(self, role_boosts: list[tuple[float, bool]]) -> None:
        role_models = [_make_boost(b, a) for b, a in role_boosts]
        calculator = XpCalculator(boost_repo=_make_repo(role_models, None, None))
        result = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_A)
        expected = 1.0
        for boost, _ in role_boosts:
            expected *= boost
        assert result == pytest.approx(expected)

    @given(
        role_boosts=boost_list,
        channel_boost=boost_pair,
    )
    @settings(max_examples=120)
    @pytest.mark.asyncio
    async def test_channel_does_not_affect_other_channel(
        self,
        role_boosts: list[tuple[float, bool]],
        channel_boost: tuple[float, bool],
    ) -> None:
        role_models = [_make_boost(b, a) for b, a in role_boosts]
        channel_model = _make_boost(*channel_boost)

        async def _get_boost(guild_id: str, entity_id: str, target=None) -> XpBoostModel | None:
            if target == BoostTarget.CHANNEL and entity_id == CHANNEL_A:
                return channel_model
            return None

        repo = MagicMock()
        repo.get_boosts_for_target = AsyncMock(return_value=role_models)
        repo.get_boost = AsyncMock(side_effect=_get_boost)
        calculator = XpCalculator(boost_repo=repo)

        with_channel = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_A)
        without_channel = await calculator.get_effective_boost(GUID, USER_ID, ROLE_IDS, CHANNEL_B)
        assert with_channel >= without_channel
        assert without_channel == pytest.approx(_expected_boost(role_boosts, None, None))

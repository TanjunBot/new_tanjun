"""Tests for repositories/xp_boost_repository.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from models import XpBoostModel
from repositories.xp_boost_repository import BoostTarget, XpBoostRepository
from tests.helpers.factories import xp_boost_row


@pytest.fixture
def repo() -> XpBoostRepository:
    return XpBoostRepository()


class TestBoostTarget:
    def test_role_table(self):
        assert BoostTarget.ROLE.table == "roleXpBoost"
        assert BoostTarget.ROLE.entity_column == "role_id"

    def test_channel_table(self):
        assert BoostTarget.CHANNEL.table == "channelXpBoost"

    def test_user_table(self):
        assert BoostTarget.USER.table == "userXpBoost"


class TestXpBoostRepository:
    @pytest.mark.asyncio
    async def test_add_boost(self, repo: XpBoostRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.add_boost("123", "456", 2.0, True, BoostTarget.USER)
            mock_exec.assert_awaited_once()
            query = mock_exec.await_args[0][0]
            assert "userXpBoost" in query
            assert "ON DUPLICATE KEY UPDATE" in query

    @pytest.mark.asyncio
    async def test_remove_boost(self, repo: XpBoostRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.remove_boost("123", "456", BoostTarget.ROLE)
            mock_exec.assert_awaited_once()
            assert "DELETE FROM roleXpBoost" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_boost_found(self, repo: XpBoostRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [xp_boost_row(3.0, False)]
            result = await repo.get_boost("123", "456", BoostTarget.CHANNEL)
            assert result == XpBoostModel(boost=3.0, additive=False)

    @pytest.mark.asyncio
    async def test_get_boost_none(self, repo: XpBoostRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_boost("123", "456")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_boosts_for_target_empty_ids(self, repo: XpBoostRepository):
        result = await repo.get_boosts_for_target("123", [], BoostTarget.ROLE)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_boosts_for_target(self, repo: XpBoostRepository):
        async def fake_iter(*args, **kwargs):
            yield xp_boost_row(2.0, True)
            yield xp_boost_row(1.5, False)

        with patch.object(XpBoostModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await repo.get_boosts_for_target("123", ["111", "222"], BoostTarget.ROLE)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_boosts(self, repo: XpBoostRepository):
        call_count = 0

        async def fake_iter(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                yield xp_boost_row(2.0, True)
            return
            yield

        with patch.object(XpBoostModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await repo.get_all_boosts("123")
        assert "roles" in result
        assert "channels" in result
        assert "users" in result

    def test_singleton_exists(self):
        from repositories.xp_boost_repository import xp_boost_repo

        assert isinstance(xp_boost_repo, XpBoostRepository)

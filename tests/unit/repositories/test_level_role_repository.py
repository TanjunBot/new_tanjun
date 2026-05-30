"""Tests for repositories/level_role_repository.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from models import LevelRoleModel
from repositories.level_role_repository import LevelRoleRepository
from tests.helpers.factories import ROLE_ID, level_role_row


@pytest.fixture
def repo() -> LevelRoleRepository:
    return LevelRoleRepository()


class TestLevelRoleRepositoryGroupByLevel:
    def test_single_level(self):
        roles = [
            LevelRoleModel.from_row(level_role_row(5, ROLE_ID)),
            LevelRoleModel.from_row(level_role_row(5, "88888888888888888")),
        ]
        groups = LevelRoleRepository.group_by_level(roles)
        assert len(groups) == 1
        assert groups[0].level == 5
        assert groups[0].role_ids == [ROLE_ID, "88888888888888888"]

    def test_multiple_levels_sorted(self):
        roles = [
            LevelRoleModel.from_row(level_role_row(10, "99999999999999999")),
            LevelRoleModel.from_row(level_role_row(5, ROLE_ID)),
        ]
        groups = LevelRoleRepository.group_by_level(roles)
        assert groups[0].level == 5
        assert groups[1].level == 10

    def test_empty_list(self):
        assert LevelRoleRepository.group_by_level([]) == []


class TestLevelRoleRepository:
    @pytest.mark.asyncio
    async def test_assign(self, repo: LevelRoleRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.assign("123", "777", 10)
            mock_exec.assert_awaited_once()
            assert "levelRole" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_unassign(self, repo: LevelRoleRepository):
        with patch("api.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.unassign("123", "777")
            assert "DELETE FROM levelRole" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_by_role_found(self, repo: LevelRoleRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(10,)]
            result = await repo.get_by_role("123", "777")
            assert result == 10

    @pytest.mark.asyncio
    async def test_get_by_role_none(self, repo: LevelRoleRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_by_role("123", "777")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repo: LevelRoleRepository):
        async def fake_iter(*args, **kwargs):
            yield LevelRoleModel.from_row(level_role_row(5, ROLE_ID))

        with patch.object(LevelRoleModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            roles = [r async for r in repo.get_all("123")]
        assert len(roles) == 1

    @pytest.mark.asyncio
    async def test_get_grouped_by_level(self, repo: LevelRoleRepository):
        async def fake_iter(*args, **kwargs):
            yield LevelRoleModel.from_row(level_role_row(5, ROLE_ID))
            yield LevelRoleModel.from_row(level_role_row(10, "99999999999999999"))

        with patch.object(LevelRoleModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            groups = await repo.get_grouped_by_level("123")
        assert len(groups) == 2

    @pytest.mark.asyncio
    async def test_get_roles_for_level(self, repo: LevelRoleRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("777",), ("888",)]
            result = await repo.get_roles_for_level("123", 5)
            assert result == ["777", "888"]

    @pytest.mark.asyncio
    async def test_get_roles_for_level_empty(self, repo: LevelRoleRepository):
        with patch("api.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_roles_for_level("123", 5)
            assert result == []

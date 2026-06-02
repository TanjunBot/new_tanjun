"""Tests for logUserBlacklist schema repair on blacklist checks."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from repositories.log_blacklist_repository import LogBlacklistRepository, LogBlacklistType  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_is_entity_blacklisted_ensures_log_user_blacklist_schema() -> None:
    ensure = AsyncMock()
    repo = LogBlacklistRepository()
    with (
        patch("utils.schema_ensure.ensure_table_schema", new=ensure),
        patch("api.execute_query", new=AsyncMock(return_value=[])),
    ):
        result = await repo.is_entity_blacklisted("1", "2", LogBlacklistType.USER)
    ensure.assert_awaited_once_with("logUserBlacklist")
    assert result is None

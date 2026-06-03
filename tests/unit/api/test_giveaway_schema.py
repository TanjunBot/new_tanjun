"""Tests for giveaway schema repair on API access."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import get_giveaway  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_giveaway_ensures_schema() -> None:
    ensure = AsyncMock()
    service = MagicMock()
    service.get = AsyncMock(return_value=None)
    with (
        patch("utils.schema_ensure.ensure_table_schema", new=ensure),
        patch("services.giveaway_service.giveaway_service", service),
    ):
        result = await get_giveaway(1)
    ensure.assert_awaited_once_with("giveaway")
    assert result is None

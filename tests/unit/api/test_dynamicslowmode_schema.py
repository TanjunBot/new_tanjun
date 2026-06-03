"""Tests for dynamicslowmode schema repair on API access."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import get_dynamicslowmode, get_dynamicslowmode_channels  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_dynamicslowmode_channels_ensures_schema() -> None:
    ensure = AsyncMock()

    async def empty_iter(*_a, **_k):
        if False:
            yield

    with (
        patch("utils.schema_ensure.ensure_table_schema", new=ensure),
        patch(
            "models.DynamicSlowmodeModel.iter_rows",
            return_value=empty_iter(),
        ),
    ):
        result = await get_dynamicslowmode_channels("1")
    ensure.assert_awaited_once_with("dynamicslowmode")
    assert result == []


@pytest.mark.asyncio
async def test_get_dynamicslowmode_ensures_schema() -> None:
    ensure = AsyncMock()
    with (
        patch("utils.schema_ensure.ensure_table_schema", new=ensure),
        patch("api.execute_query", new=AsyncMock(return_value=[])),
    ):
        result = await get_dynamicslowmode("99")
    ensure.assert_awaited_once_with("dynamicslowmode")
    assert result is None

"""Tests for mediaChannel schema repair on API access."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import add_media_channel, get_media_channel  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_media_channel_ensures_schema_before_query() -> None:
    ensure = AsyncMock()
    with (
        patch("utils.schema_ensure.ensure_table_schema", new=ensure),
        patch("api.execute_query", new=AsyncMock(return_value=[])),
    ):
        result = await get_media_channel("123")
    ensure.assert_awaited_once_with("mediaChannel")
    assert result is False


@pytest.mark.asyncio
async def test_add_media_channel_ensures_schema_before_insert() -> None:
    ensure = AsyncMock()
    with (
        patch("utils.schema_ensure.ensure_table_schema", new=ensure),
        patch("api.execute_action", new=AsyncMock(return_value=True)),
    ):
        await add_media_channel("1", "2")
    ensure.assert_awaited_once_with("mediaChannel")

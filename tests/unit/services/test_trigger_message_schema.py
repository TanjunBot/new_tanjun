"""Tests for triggerMessages schema repair before matching."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from services.trigger_message_service import TriggerMessageService  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_match_ensures_trigger_messages_schema() -> None:
    ensure = AsyncMock()
    with (
        patch("utils.schema_ensure.ensure_table_schema", new=ensure),
        patch("api.execute_query", new=AsyncMock(return_value=[])),
    ):
        result = await TriggerMessageService().match("1", "hello", "2")
    ensure.assert_awaited_once_with("triggerMessages")
    assert result is None

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from utils.command_tree_sync import (
    count_tree_leaves,
    format_sync_http_error,
    is_primary_sync_shard,
    sync_application_commands,
)

def test_format_sync_http_error_includes_status_and_body() -> None:
    exc = discord.HTTPException(MagicMock(), {"message": "Invalid Form Body"})
    exc.status = 400
    exc.code = 50035
    formatted = format_sync_http_error(exc)
    assert "400" in formatted
    assert "50035" in formatted


def test_is_primary_sync_shard() -> None:
    bot = MagicMock()
    bot.shard_id = None
    assert is_primary_sync_shard(bot) is True
    bot.shard_id = 0
    assert is_primary_sync_shard(bot) is True
    bot.shard_id = 1
    assert is_primary_sync_shard(bot) is False


@pytest.mark.asyncio
async def test_sync_application_commands_returns_counts() -> None:
    bot = MagicMock()
    leaf = MagicMock()
    bot.tree.walk_commands.return_value = [leaf, leaf]
    synced_cmd = MagicMock()
    bot.tree.sync = AsyncMock(return_value=[synced_cmd])
    result = await sync_application_commands(bot)
    assert result.synced_count == 1
    assert result.tree_leaf_count == 2
    bot.tree.sync.assert_awaited_once()


def test_count_tree_leaves() -> None:
    tree = MagicMock()
    tree.walk_commands.return_value = [MagicMock(), MagicMock(), MagicMock()]
    assert count_tree_leaves(tree) == 3

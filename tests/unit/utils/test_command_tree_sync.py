from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from utils.command_tree_sync import (
    CommandSyncResult,
    count_tree_leaves,
    format_sync_http_error,
    is_primary_sync_shard,
    sync_application_commands,
    sync_application_commands_safe,
)


def test_format_sync_http_error_includes_status_and_body() -> None:
    exc = discord.HTTPException(MagicMock(), {"message": "Invalid Form Body"})
    exc.status = 400
    exc.code = 50035
    formatted = format_sync_http_error(exc)
    assert "400" in formatted
    assert "50035" in formatted


def test_format_sync_http_error_includes_text_and_dict_body() -> None:
    response = MagicMock()
    response.text = "bad request"
    exc = discord.HTTPException(response, {"message": "Invalid"})
    exc.status = 400
    exc.code = 50035
    exc.text = "bad request"
    exc.body = {"details": "x"}
    formatted = format_sync_http_error(exc)
    assert "400" in formatted
    assert "50035" in formatted
    assert "bad request" in formatted
    assert '"details": "x"' in formatted


def test_format_sync_http_error_string_body() -> None:
    response = MagicMock()
    response.text = None
    exc = discord.HTTPException(response, "plain text")
    exc.status = 500
    exc.code = None
    exc.text = None
    exc.body = "plain text"
    formatted = format_sync_http_error(exc)
    assert "500" in formatted
    assert "plain text" in formatted


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


@pytest.mark.asyncio
async def test_sync_application_commands_missing_tree() -> None:
    bot = MagicMock()
    bot.tree = None
    with pytest.raises(RuntimeError, match="no application command tree"):
        await sync_application_commands(bot)


@pytest.mark.asyncio
async def test_sync_application_commands_with_custom_tree() -> None:
    bot = MagicMock()
    tree = MagicMock()
    tree.walk_commands.return_value = [MagicMock()]
    tree.sync = AsyncMock(return_value=[MagicMock()])
    result = await sync_application_commands(bot, tree=tree)
    assert result.synced_count == 1
    assert result.tree_leaf_count == 1


@pytest.mark.asyncio
async def test_sync_application_commands_safe_success() -> None:
    bot = MagicMock()
    tree = MagicMock()
    tree.walk_commands.return_value = [MagicMock()]
    tree.sync = AsyncMock(return_value=[MagicMock()])
    result = await sync_application_commands_safe(bot, tree=tree)
    assert isinstance(result, CommandSyncResult)
    assert result.synced_count == 1


@pytest.mark.asyncio
async def test_sync_application_commands_safe_http_exception() -> None:
    bot = MagicMock()
    tree = MagicMock()
    tree.walk_commands.return_value = [MagicMock()]
    response = MagicMock()
    response.text = "error"
    exc = discord.HTTPException(response, "error")
    exc.status = 400
    exc.code = 50035
    exc.text = "error"
    exc.body = None
    tree.sync = AsyncMock(side_effect=exc)
    with pytest.raises(discord.HTTPException):
        await sync_application_commands_safe(bot, tree=tree)


@pytest.mark.asyncio
async def test_sync_application_commands_safe_generic_exception() -> None:
    bot = MagicMock()
    tree = MagicMock()
    tree.walk_commands.return_value = [MagicMock()]
    tree.sync = AsyncMock(side_effect=RuntimeError("boom"))
    with pytest.raises(RuntimeError, match="boom"):
        await sync_application_commands_safe(bot, tree=tree)


def test_count_tree_leaves() -> None:
    tree = MagicMock()
    tree.walk_commands.return_value = [MagicMock(), MagicMock(), MagicMock()]
    assert count_tree_leaves(tree) == 3

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CommandSyncResult:
    synced_count: int
    tree_leaf_count: int
    duration_sec: float
    synced: list[discord.app_commands.AppCommand]


def count_tree_leaves(tree: discord.app_commands.CommandTree[Any]) -> int:
    return sum(1 for _ in tree.walk_commands())


def format_sync_http_error(exc: discord.HTTPException) -> str:
    parts = [f"HTTP {exc.status}"]
    code = getattr(exc, "code", None)
    if code is not None:
        parts.append(f"code={code}")
    text = getattr(exc, "text", None)
    if text:
        parts.append(str(text))
    body = getattr(exc, "body", None)
    if body is not None and body not in (text, ""):
        if isinstance(body, (dict, list)):
            parts.append(json.dumps(body, ensure_ascii=False)[:500])
        else:
            parts.append(str(body)[:500])
    return " ".join(parts)


def is_primary_sync_shard(bot: commands.Bot) -> bool:
    shard_id = getattr(bot, "shard_id", None)
    return shard_id is None or shard_id == 0


async def sync_application_commands(
    bot: commands.Bot,
    *,
    tree: discord.app_commands.CommandTree[Any] | None = None,
) -> CommandSyncResult:
    active_tree = tree or bot.tree
    if active_tree is None:
        raise RuntimeError("Bot has no application command tree")

    tree_leaf_count = count_tree_leaves(active_tree)
    started = time.monotonic()
    synced = await active_tree.sync()
    duration_sec = round(time.monotonic() - started, 2)

    if len(synced) != tree_leaf_count:
        logger.warning(
            "Command sync count mismatch: Discord returned %s root command(s), tree has %s leaf command(s)",
            len(synced),
            tree_leaf_count,
        )

    return CommandSyncResult(
        synced_count=len(synced),
        tree_leaf_count=tree_leaf_count,
        duration_sec=duration_sec,
        synced=synced,
    )


async def sync_application_commands_safe(
    bot: commands.Bot,
    *,
    tree: discord.app_commands.CommandTree[Any] | None = None,
) -> CommandSyncResult | None:
    try:
        result = await sync_application_commands(bot, tree=tree)
    except discord.HTTPException as exc:
        logger.error("Application command sync failed: %s", format_sync_http_error(exc))
        raise
    except Exception:
        logger.exception("Application command sync failed")
        raise
    else:
        logger.info(
            "Application commands synced: %s root command(s), %s tree leaf command(s), %.2fs",
            result.synced_count,
            result.tree_leaf_count,
            result.duration_sec,
        )
        return result

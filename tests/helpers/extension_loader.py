from __future__ import annotations

import asyncio
import contextlib
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from api import set_bot
from tests.helpers.db import make_mock_pool


class _LoopProxy:
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._tasks: list[asyncio.Task[Any]] = []

    def create_task(self, coro: Any, *, name: str | None = None) -> asyncio.Task[Any]:
        task = self._loop.create_task(coro, name=name)
        self._tasks.append(task)
        return task

    def __getattr__(self, name: str) -> Any:
        return getattr(self._loop, name)


EXTENSION_NAMES = [
    "extensions.admin",
    "extensions.administration",
    "extensions.ai",
    "extensions.channel",
    "extensions.error_handler",
    "extensions.fun",
    "extensions.games",
    "extensions.giveaway",
    "extensions.health_check",
    "extensions.image",
    "extensions.level",
    "extensions.listeners",
    "extensions.loops",
    "extensions.logs",
    "extensions.math",
    "extensions.minigames",
    "extensions.setup_wizards",
    "extensions.utility",
]


async def load_extension(bot: MagicMock, extension: str) -> Any:
    import importlib

    module = importlib.import_module(extension)
    if hasattr(module, "setup"):
        await module.setup(bot)
    return module


def make_bot_for_extensions(pool: MagicMock | None = None) -> MagicMock:
    if pool is None:
        pool, _, _ = make_mock_pool()
    bot = MagicMock()
    bot._pool = pool
    bot._pool_ready = asyncio.Event()
    bot._pool_ready.set()
    bot._tree_commands = []
    bot._loop_proxy: _LoopProxy | None = None

    def _add_command(cmd: Any) -> None:
        bot._tree_commands.append(cmd)

    bot.tree = MagicMock()
    bot.tree.add_command = MagicMock(side_effect=_add_command)
    bot.tree.remove_command = MagicMock()
    bot.tree.get_commands = MagicMock(side_effect=lambda: list(bot._tree_commands))
    bot.tree.walk_commands = MagicMock(return_value=[])
    bot.tree.on_error = None
    bot.load_extension = AsyncMock()
    bot.cogs = {}

    async def _add_cog(cog: Any) -> None:
        bot.cogs[cog.__class__.__name__] = cog
        # Register app commands defined on the cog via @app_commands.command
        for cmd in getattr(cog, "__cog_app_commands__", []):
            bot.tree.add_command(cmd)

    bot.add_cog = AsyncMock(side_effect=_add_cog)
    bot.get_cog = lambda name: bot.cogs.get(name)
    bot.user = MagicMock()
    bot.user.id = 999999999
    set_bot(bot)
    return bot


def _wire_bot_loop(bot: MagicMock) -> None:
    running_loop = asyncio.get_running_loop()
    loop_proxy = getattr(bot, "_loop_proxy", None)
    if loop_proxy is None:
        loop_proxy = _LoopProxy(running_loop)
        bot._loop_proxy = loop_proxy
    bot.loop = loop_proxy


async def fire_cog_on_ready(bot: MagicMock) -> None:
    if hasattr(bot._pool_ready, "set") and not bot._pool_ready.is_set():
        bot._pool_ready.set()
    _wire_bot_loop(bot)
    for cog in bot.cogs.values():
        on_ready = getattr(cog, "on_ready", None)
        if on_ready is not None:
            await on_ready()


async def teardown_extension_bot(bot: MagicMock) -> None:
    loop_proxy = getattr(bot, "_loop_proxy", None)
    if loop_proxy is not None:
        for task in list(loop_proxy._tasks):
            if not task.done():
                task.cancel()
    for cog in bot.cogs.values():
        log_task = getattr(cog, "_log_consumer_task", None)
        if log_task is not None and hasattr(log_task, "done") and not log_task.done():
            log_task.cancel()
        for attr_name in dir(cog):
            loop_obj = getattr(cog, attr_name, None)
            if loop_obj is None:
                continue
            is_running = getattr(loop_obj, "is_running", None)
            cancel = getattr(loop_obj, "cancel", None)
            if not callable(is_running) or not callable(cancel):
                continue
            with contextlib.suppress(Exception):
                if is_running():
                    cancel()
    if loop_proxy is not None and loop_proxy._tasks:
        await asyncio.gather(*loop_proxy._tasks, return_exceptions=True)
    set_bot(None)


async def build_extension_bot() -> MagicMock:
    bot = make_bot_for_extensions()
    await load_all_extensions(bot)
    await fire_cog_on_ready(bot)
    return bot


def make_bot_with_real_tree() -> Any:
    import discord
    from discord.ext import commands

    from utils.app_command_tree import make_add_command_idempotent

    intents = discord.Intents.none()
    bot = commands.Bot(command_prefix="!", intents=intents, application_id=999999999)
    make_add_command_idempotent(bot.tree)
    bot._pool = MagicMock()
    bot._pool_ready = asyncio.Event()
    bot._pool_ready.set()
    return bot


async def load_all_extensions(bot: MagicMock) -> list[str]:
    loaded = []
    for ext in EXTENSION_NAMES:
        try:
            await load_extension(bot, ext)
            loaded.append(ext)
        except Exception as exc:
            raise RuntimeError(f"Failed to load extension {ext!r}") from exc
    return loaded


def get_tree_commands(bot: MagicMock) -> list[Any]:
    return list(bot._tree_commands)


def get_tree_command_names(bot: MagicMock) -> list[str]:
    return [getattr(cmd, "name", str(cmd)) for cmd in get_tree_commands(bot)]


def get_subcommand_names(group: Any) -> list[str]:
    commands = getattr(group, "commands", None)
    if not commands:
        return []
    return [getattr(cmd, "name", str(cmd)) for cmd in commands]


def find_tree_group(bot: MagicMock, name: str) -> Any | None:
    for cmd in get_tree_commands(bot):
        if getattr(cmd, "name", None) == name:
            return cmd
    return None


def find_nested_group(root: Any, name: str) -> Any | None:
    for cmd in getattr(root, "commands", []):
        if getattr(cmd, "name", None) == name:
            return cmd
    return None

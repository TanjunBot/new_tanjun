from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

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
    bot = MagicMock()
    bot._pool = pool or MagicMock()
    bot._pool_ready = asyncio.Event()
    bot._pool_ready.set()
    bot._tree_commands = []

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
    bot.loop = MagicMock()
    bot.loop.create_task = MagicMock(return_value=MagicMock(done=lambda: False))

    async def _add_cog(cog: Any) -> None:
        bot.cogs[cog.__class__.__name__] = cog
        # Register app commands defined on the cog via @app_commands.command
        for cmd in getattr(cog, "__cog_app_commands__", []):
            bot.tree.add_command(cmd)

    bot.add_cog = AsyncMock(side_effect=_add_cog)
    bot.get_cog = lambda name: bot.cogs.get(name)
    bot.user = MagicMock()
    bot.user.id = 999999999
    return bot


async def fire_cog_on_ready(bot: MagicMock) -> None:
    if hasattr(bot._pool_ready, "set") and not bot._pool_ready.is_set():
        bot._pool_ready.set()
    for cog in bot.cogs.values():
        on_ready = getattr(cog, "on_ready", None)
        if on_ready is not None:
            await on_ready()


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

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tests.helpers.live_discord.discord_api import DiscordBotClient

SUB_COMMAND_TYPE = 1
SUB_COMMAND_GROUP_TYPE = 2
USER_OPTION_TYPE = 6
STRING_OPTION_TYPE = 3


@dataclass(frozen=True)
class ResolvedSubcommand:
    name: str
    type: int
    options: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ResolvedSlashCommand:
    command_id: str
    version: str
    name: str
    option_chain: tuple[dict[str, Any], ...]
    group_command: dict[str, Any]

    @property
    def subcommand(self) -> ResolvedSubcommand:
        leaf = self.option_chain[-1]
        return ResolvedSubcommand(
            name=str(leaf["name"]),
            type=int(leaf.get("type", SUB_COMMAND_TYPE)),
            options=tuple(leaf.get("options") or []),
        )


class CommandRegistry:
    def __init__(
        self,
        bot_client: DiscordBotClient,
        *,
        guild_id: str,
    ) -> None:
        self._bot_client = bot_client
        self._guild_id = guild_id
        self._commands: list[dict[str, Any]] | None = None

    async def refresh(self) -> None:
        commands = await self._bot_client.list_guild_commands(self._guild_id)
        if not commands:
            commands = await self._bot_client.list_global_commands()
        self._commands = commands

    async def _ensure_loaded(self) -> list[dict[str, Any]]:
        if self._commands is None:
            await self.refresh()
        assert self._commands is not None
        return self._commands

    async def resolve(self, *, group: str, subcommand: str) -> ResolvedSlashCommand:
        return await self.resolve_tree_path(f"{group} {subcommand}")

    async def resolve_tree_path(self, tree_path: str) -> ResolvedSlashCommand:
        parts = [part for part in tree_path.split() if part]
        if not parts:
            raise RuntimeError("Empty command tree path")
        commands = await self._ensure_loaded()
        root_cmd = _find_command_by_name(commands, parts[0])
        if root_cmd is None:
            raise RuntimeError(
                f"Application command {parts[0]!r} not found. "
                f"Available: {sorted(cmd.get('name', '') for cmd in commands)}"
            )
        chain = _resolve_option_chain(root_cmd, parts[1:])
        return ResolvedSlashCommand(
            command_id=str(root_cmd["id"]),
            version=str(root_cmd["version"]),
            name=str(root_cmd["name"]),
            option_chain=chain,
            group_command=root_cmd,
        )

    def param_name(self, resolved: ResolvedSlashCommand, *, kind: str) -> str:
        for opt in resolved.subcommand.options:
            opt_type = int(opt.get("type", 0))
            if kind == "user" and opt_type == USER_OPTION_TYPE:
                return str(opt["name"])
            if kind == "message" and opt_type == STRING_OPTION_TYPE:
                return str(opt["name"])
        if kind == "user":
            return "user"
        if kind == "message":
            return "message"
        raise RuntimeError(f"Unknown parameter kind {kind!r}")


def _find_command_by_name(
    commands: list[dict[str, Any]],
    name: str,
) -> dict[str, Any] | None:
    for cmd in commands:
        if str(cmd.get("name", "")) == name:
            return cmd
    return None


def _find_named_option(
    options: list[dict[str, Any]],
    name: str,
) -> dict[str, Any] | None:
    for opt in options:
        if int(opt.get("type", 0)) not in (SUB_COMMAND_TYPE, SUB_COMMAND_GROUP_TYPE):
            continue
        if str(opt.get("name", "")) == name:
            return opt
    return None


def _resolve_option_chain(
    root_cmd: dict[str, Any],
    parts: list[str],
) -> tuple[dict[str, Any], ...]:
    if not parts:
        raise RuntimeError(f"Command {root_cmd.get('name')!r} has no subcommand path")
    chain: list[dict[str, Any]] = []
    current_options = list(root_cmd.get("options") or [])
    for index, part in enumerate(parts):
        match = _find_named_option(current_options, part)
        if match is None:
            available = [
                str(opt.get("name", ""))
                for opt in current_options
                if int(opt.get("type", 0)) in (SUB_COMMAND_TYPE, SUB_COMMAND_GROUP_TYPE)
            ]
            raise RuntimeError(
                f"Option {part!r} not found under {root_cmd.get('name')!r}. "
                f"Available: {available}"
            )
        chain.append(match)
        is_leaf = index == len(parts) - 1
        if is_leaf and int(match.get("type", 0)) != SUB_COMMAND_TYPE:
            raise RuntimeError(f"Leaf option {part!r} is not a subcommand")
        current_options = list(match.get("options") or [])
    return tuple(chain)


def _find_subcommand_option(
    group_cmd: dict[str, Any],
    subcommand: str,
) -> dict[str, Any] | None:
    return _find_named_option(list(group_cmd.get("options") or []), subcommand)

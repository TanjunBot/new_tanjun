from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import discord
from discord.ext import commands

DISCORD_COMMAND_PAYLOAD_LIMIT = 8000
DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT = 7500


@dataclass(frozen=True, slots=True)
class CommandPayloadAudit:
    command_name: str
    payload_bytes: int
    over_safe_limit: bool
    over_hard_limit: bool


def _command_payload_bytes(command: discord.app_commands.Command[Any, Any, Any], tree: discord.app_commands.CommandTree[Any]) -> int:
    payload = command.to_dict(tree)
    return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def audit_root_command_payloads(
    bot: commands.Bot,
    *,
    safe_limit: int = DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT,
    hard_limit: int = DISCORD_COMMAND_PAYLOAD_LIMIT,
) -> list[CommandPayloadAudit]:
    tree = bot.tree

    results: list[CommandPayloadAudit] = []
    for command in tree.get_commands():
        if not isinstance(command, discord.app_commands.Command):
            continue
        payload_bytes = _command_payload_bytes(command, tree)
        results.append(
            CommandPayloadAudit(
                command_name=str(command.name),
                payload_bytes=payload_bytes,
                over_safe_limit=payload_bytes > safe_limit,
                over_hard_limit=payload_bytes > hard_limit,
            )
        )
    return results


def find_oversized_root_commands(
    bot: commands.Bot,
    *,
    safe_limit: int = DISCORD_COMMAND_PAYLOAD_SAFE_LIMIT,
) -> list[CommandPayloadAudit]:
    return [entry for entry in audit_root_command_payloads(bot, safe_limit=safe_limit) if entry.over_safe_limit]

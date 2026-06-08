from __future__ import annotations

import uuid
from typing import Any

from tests.helpers.live_discord.command_registry import (
    SUB_COMMAND_GROUP_TYPE,
    SUB_COMMAND_TYPE,
    ResolvedSlashCommand,
)
from tests.helpers.live_discord.discord_api import GuildContext
from tests.helpers.live_discord.interaction_payload import (
    APPLICATION_COMMAND_TYPE,
    CHAT_INPUT_COMMAND_TYPE,
    discord_nonce,
)

STRING_OPTION_TYPE = 3
INTEGER_OPTION_TYPE = 4
BOOLEAN_OPTION_TYPE = 5
USER_OPTION_TYPE = 6
CHANNEL_OPTION_TYPE = 7
ROLE_OPTION_TYPE = 8
MENTIONABLE_OPTION_TYPE = 9
NUMBER_OPTION_TYPE = 10
ATTACHMENT_OPTION_TYPE = 11


def _choice_value(option: dict[str, Any]) -> Any:
    choices = option.get("choices") or []
    if not choices:
        return None
    first = choices[0]
    return first.get("value", first.get("name"))


def _smoke_value_for_option(
    option: dict[str, Any],
    *,
    guild: GuildContext,
    bot_user_id: str,
) -> Any | None:
    opt_type = int(option.get("type", 0))
    if opt_type == STRING_OPTION_TYPE:
        choice = _choice_value(option)
        if choice is not None:
            return str(choice)
        max_len = option.get("max_length")
        value = "e2e"
        if isinstance(max_len, int) and max_len < len(value):
            return "x" * max(1, max_len)
        return value
    if opt_type == INTEGER_OPTION_TYPE:
        choice = _choice_value(option)
        if choice is not None:
            return int(choice)
        min_value = option.get("min_value")
        return int(min_value) if min_value is not None else 1
    if opt_type == NUMBER_OPTION_TYPE:
        choice = _choice_value(option)
        if choice is not None:
            return float(choice)
        return 1.0
    if opt_type == BOOLEAN_OPTION_TYPE:
        return True
    if opt_type == USER_OPTION_TYPE:
        return guild.owner_user_id
    if opt_type == CHANNEL_OPTION_TYPE:
        return guild.channel_id
    if opt_type in (ROLE_OPTION_TYPE, MENTIONABLE_OPTION_TYPE):
        return guild.owner_user_id
    if opt_type == ATTACHMENT_OPTION_TYPE:
        return None
    return None


def _leaf_param_options(
    resolved: ResolvedSlashCommand,
    *,
    guild: GuildContext,
    bot_user_id: str,
) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    for option in resolved.subcommand.options:
        opt_type = int(option.get("type", 0))
        if opt_type in (SUB_COMMAND_TYPE, SUB_COMMAND_GROUP_TYPE):
            continue
        if not option.get("required", False):
            continue
        value = _smoke_value_for_option(option, guild=guild, bot_user_id=bot_user_id)
        if value is None:
            continue
        params.append({"type": opt_type, "name": str(option["name"]), "value": value})
    return params


def _nest_option_chain(
    chain: tuple[dict[str, Any], ...],
    leaf_options: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not chain:
        return leaf_options

    def build(level: int) -> list[dict[str, Any]]:
        node = chain[level]
        inner = leaf_options if level == len(chain) - 1 else build(level + 1)
        return [
            {
                "type": int(node.get("type", SUB_COMMAND_TYPE)),
                "name": str(node["name"]),
                "options": inner,
            }
        ]

    return build(0)


def build_smoke_interaction_payload(
    resolved: ResolvedSlashCommand,
    *,
    application_id: str,
    guild: GuildContext,
    bot_user_id: str,
) -> dict[str, Any]:
    leaf_options = _leaf_param_options(resolved, guild=guild, bot_user_id=bot_user_id)
    nested = _nest_option_chain(resolved.option_chain, leaf_options)
    return {
        "type": APPLICATION_COMMAND_TYPE,
        "application_id": application_id,
        "guild_id": guild.guild_id,
        "channel_id": guild.channel_id,
        "session_id": uuid.uuid4().hex,
        "nonce": discord_nonce(),
        "data": {
            "version": resolved.version,
            "id": resolved.command_id,
            "name": resolved.name,
            "type": CHAT_INPUT_COMMAND_TYPE,
            "options": nested,
            "application_command": resolved.group_command,
            "attachments": [],
        },
    }

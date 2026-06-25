from __future__ import annotations

import uuid
from dataclasses import dataclass
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
from tests.helpers.live_discord.smoke_payload import (
    ATTACHMENT_OPTION_TYPE,
    BOOLEAN_OPTION_TYPE,
    CHANNEL_OPTION_TYPE,
    INTEGER_OPTION_TYPE,
    MENTIONABLE_OPTION_TYPE,
    NUMBER_OPTION_TYPE,
    ROLE_OPTION_TYPE,
    STRING_OPTION_TYPE,
    USER_OPTION_TYPE,
    _choice_value,
    _nest_option_chain,
)
from tests.helpers.live_e2e.models import CommandLiveCase


@dataclass(frozen=True)
class PayloadContext:
    guild: GuildContext
    bot_user_id: str
    secondary_user_id: str | None = None
    disposable_channel_id: str | None = None
    attachment_id: str | None = None
    temp_role_id: str | None = None


def _context_value_for_option(
    option: dict[str, Any],
    *,
    ctx: PayloadContext,
) -> Any | None:
    opt_type = int(option.get("type", 0))
    name = str(option.get("name", "")).lower()
    if opt_type == STRING_OPTION_TYPE:
        choice = _choice_value(option)
        if choice is not None:
            return str(choice)
        max_len = option.get("max_length")
        if "equation" in name or "expression" in name or "func" in name:
            value = "2+2"
        elif "prompt" in name or "situation" in name:
            value = "e2e test"
        elif "twitch" in name:
            value = "shroud"
        elif "tag" in name:
            value = "#ABC123"
        elif "emoji" in name:
            value = "😀"
        elif "imageurl" in name or "url" in name:
            value = "https://example.com/e2e.png"
        else:
            value = "e2e"
        if isinstance(max_len, int) and max_len < len(value):
            return "x" * max(1, max_len)
        return value
    if opt_type == INTEGER_OPTION_TYPE:
        choice = _choice_value(option)
        if choice is not None:
            return int(choice)
        min_value = option.get("min_value")
        if "duration" in name or "seconds" in name:
            return 60
        if "amount" in name or "messages" in name or "limit" in name:
            return 5
        return int(min_value) if min_value is not None else 1
    if opt_type == NUMBER_OPTION_TYPE:
        choice = _choice_value(option)
        if choice is not None:
            return float(choice)
        return 1.0
    if opt_type == BOOLEAN_OPTION_TYPE:
        return True
    if opt_type == USER_OPTION_TYPE:
        if ctx.secondary_user_id and name in {"user", "member", "target", "opponent", "player"}:
            return ctx.secondary_user_id
        return ctx.guild.owner_user_id
    if opt_type == CHANNEL_OPTION_TYPE:
        if ctx.disposable_channel_id and name in {"channel", "category"}:
            return ctx.disposable_channel_id
        return ctx.guild.channel_id
    if opt_type in (ROLE_OPTION_TYPE, MENTIONABLE_OPTION_TYPE):
        return ctx.temp_role_id or ctx.guild.owner_user_id
    if opt_type == ATTACHMENT_OPTION_TYPE:
        return ctx.attachment_id
    return None


def _leaf_param_options(
    resolved: ResolvedSlashCommand,
    *,
    case: CommandLiveCase,
    ctx: PayloadContext,
) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    for option in resolved.subcommand.options:
        opt_type = int(option.get("type", 0))
        if opt_type in (SUB_COMMAND_TYPE, SUB_COMMAND_GROUP_TYPE):
            continue
        name = str(option["name"])
        if not option.get("required", False) and name not in case.option_overrides:
            continue
        if name in case.option_overrides:
            value = case.option_overrides[name]
        else:
            value = _context_value_for_option(option, ctx=ctx)
        if value is None:
            continue
        params.append({"type": opt_type, "name": name, "value": value})
    return params


def build_command_interaction_payload(
    resolved: ResolvedSlashCommand,
    *,
    application_id: str,
    case: CommandLiveCase,
    ctx: PayloadContext,
) -> dict[str, Any]:
    leaf_options = _leaf_param_options(resolved, case=case, ctx=ctx)
    nested = _nest_option_chain(resolved.option_chain, leaf_options)
    attachments_meta: list[dict[str, Any]] = []
    if ctx.attachment_id:
        attachments_meta.append(
            {
                "id": ctx.attachment_id,
                "filename": "test.png",
            }
        )
    return {
        "type": APPLICATION_COMMAND_TYPE,
        "application_id": application_id,
        "guild_id": ctx.guild.guild_id,
        "channel_id": ctx.guild.channel_id,
        "session_id": uuid.uuid4().hex,
        "nonce": discord_nonce(),
        "data": {
            "version": resolved.version,
            "id": resolved.command_id,
            "name": resolved.name,
            "type": CHAT_INPUT_COMMAND_TYPE,
            "options": nested,
            "application_command": resolved.group_command,
            "attachments": attachments_meta,
        },
    }

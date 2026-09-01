from __future__ import annotations

import time
import uuid
from typing import Any

from tests.helpers.live_discord.command_registry import ResolvedSlashCommand
from tests.helpers.live_discord.discord_api import GuildContext

DISCORD_EPOCH_MS = 1420070400000
APPLICATION_COMMAND_TYPE = 2
CHAT_INPUT_COMMAND_TYPE = 1
SUB_COMMAND_TYPE = 1
USER_OPTION_TYPE = 6
STRING_OPTION_TYPE = 3


def discord_nonce() -> str:
    timestamp_ms = int(time.time() * 1000) - DISCORD_EPOCH_MS
    return str(timestamp_ms << 22)


def build_fun_interaction_payload(
    resolved: ResolvedSlashCommand,
    *,
    application_id: str,
    guild: GuildContext,
    target_user_id: str,
    message: str | None,
    user_param_name: str = "user",
    message_param_name: str = "message",
) -> dict[str, Any]:
    sub_options: list[dict[str, Any]] = [
        {"type": USER_OPTION_TYPE, "name": user_param_name, "value": target_user_id},
    ]
    if message is not None:
        sub_options.append(
            {"type": STRING_OPTION_TYPE, "name": message_param_name, "value": message},
        )

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
            "options": [
                {
                    "type": SUB_COMMAND_TYPE,
                    "name": resolved.subcommand.name,
                    "options": sub_options,
                },
            ],
            "application_command": resolved.group_command,
            "attachments": [],
        },
    }

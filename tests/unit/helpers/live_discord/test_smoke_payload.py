from __future__ import annotations

import pytest

from tests.helpers.live_discord.command_registry import (
    SUB_COMMAND_GROUP_TYPE,
    SUB_COMMAND_TYPE,
    CommandRegistry,
)
from tests.helpers.live_discord.discord_api import GuildContext
from tests.helpers.live_discord.smoke_payload import build_smoke_interaction_payload


class _FakeBotClient:
    def __init__(self, commands: list[dict]) -> None:
        self._commands = commands

    async def list_guild_commands(self, guild_id: str) -> list[dict]:
        return self._commands

    async def list_global_commands(self) -> list[dict]:
        return []


NESTED_FIXTURE = [
    {
        "id": "2001",
        "version": "3001",
        "name": "ai_name",
        "type": 1,
        "options": [
            {
                "type": SUB_COMMAND_GROUP_TYPE,
                "name": "ai_customsituations_name",
                "options": [
                    {
                        "type": SUB_COMMAND_TYPE,
                        "name": "ai_createcustom_name",
                        "options": [
                            {"type": 3, "name": "situation", "required": True},
                        ],
                    },
                ],
            },
        ],
    },
]


@pytest.mark.asyncio
async def test_resolve_nested_tree_path() -> None:
    registry = CommandRegistry(_FakeBotClient(NESTED_FIXTURE), guild_id="1")
    resolved = await registry.resolve_tree_path(
        "ai_name ai_customsituations_name ai_createcustom_name"
    )
    assert resolved.name == "ai_name"
    assert len(resolved.option_chain) == 2
    assert resolved.subcommand.name == "ai_createcustom_name"


def test_build_smoke_payload_nested() -> None:
    registry_commands = NESTED_FIXTURE

    async def _run() -> dict:
        registry = CommandRegistry(_FakeBotClient(registry_commands), guild_id="1")
        resolved = await registry.resolve_tree_path(
            "ai_name ai_customsituations_name ai_createcustom_name"
        )
        guild = GuildContext(guild_id="1", channel_id="2", owner_user_id="9")
        return build_smoke_interaction_payload(
            resolved,
            application_id="app",
            guild=guild,
            bot_user_id="8",
        )

    import asyncio

    payload = asyncio.run(_run())
    options = payload["data"]["options"]
    assert options[0]["name"] == "ai_customsituations_name"
    assert options[0]["options"][0]["name"] == "ai_createcustom_name"
    leaf_opts = options[0]["options"][0]["options"]
    assert leaf_opts[0] == {"type": 3, "name": "situation", "value": "e2e"}

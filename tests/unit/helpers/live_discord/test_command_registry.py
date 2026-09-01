from __future__ import annotations

import pytest

from tests.helpers.live_discord.command_registry import CommandRegistry, SUB_COMMAND_TYPE


class _FakeBotClient:
    def __init__(self, commands: list[dict]) -> None:
        self._commands = commands

    async def list_guild_commands(self, guild_id: str) -> list[dict]:
        return self._commands

    async def list_global_commands(self) -> list[dict]:
        return []


FUN_GROUP_FIXTURE = [
    {
        "id": "1001",
        "version": "2001",
        "name": "funcmd_name",
        "type": 1,
        "options": [
            {
                "type": SUB_COMMAND_TYPE,
                "name": "fun_hug_name",
                "options": [
                    {"type": 6, "name": "user", "required": True},
                    {"type": 3, "name": "message", "required": False},
                ],
            },
            {
                "type": SUB_COMMAND_TYPE,
                "name": "fun_kiss_name",
                "options": [
                    {"type": 6, "name": "user", "required": True},
                    {"type": 3, "name": "message", "required": False},
                ],
            },
        ],
    },
]


@pytest.mark.asyncio
async def test_resolve_fun_subcommand() -> None:
    registry = CommandRegistry(_FakeBotClient(FUN_GROUP_FIXTURE), guild_id="1")
    resolved = await registry.resolve(group="funcmd_name", subcommand="fun_hug_name")
    assert resolved.command_id == "1001"
    assert resolved.version == "2001"
    assert resolved.name == "funcmd_name"
    assert resolved.subcommand.name == "fun_hug_name"
    assert registry.param_name(resolved, kind="user") == "user"
    assert registry.param_name(resolved, kind="message") == "message"


@pytest.mark.asyncio
async def test_resolve_missing_group() -> None:
    registry = CommandRegistry(_FakeBotClient([]), guild_id="1")
    with pytest.raises(RuntimeError, match="funcmd_name"):
        await registry.resolve(group="funcmd_name", subcommand="fun_hug_name")


@pytest.mark.asyncio
async def test_resolve_missing_subcommand() -> None:
    registry = CommandRegistry(_FakeBotClient(FUN_GROUP_FIXTURE), guild_id="1")
    with pytest.raises(RuntimeError, match="fun_wave_name"):
        await registry.resolve(group="funcmd_name", subcommand="fun_wave_name")

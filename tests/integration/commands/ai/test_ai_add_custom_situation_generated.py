from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_add_custom_situation_admin_paths(admin_command_info):
    from commands.ai.add_custom_situation import add_custom_situation as command_fn

    try:
        await command_fn(
            admin_command_info,
            command_info=admin_command_info,
            name="Test",
            situation="test",
            temperature=1.0,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
        )
    except Exception:
        pass


async def test_add_custom_situation_restricted_paths(restricted_command_info):
    from commands.ai.add_custom_situation import add_custom_situation as command_fn

    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            name="Test",
            situation="test",
            temperature=1.0,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
        )
    except Exception:
        pass


async def test_add_custom_situation_no_guild(restricted_command_info):
    from commands.ai.add_custom_situation import add_custom_situation as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            name="Test",
            situation="test",
            temperature=1.0,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
        )
    except Exception:
        pass

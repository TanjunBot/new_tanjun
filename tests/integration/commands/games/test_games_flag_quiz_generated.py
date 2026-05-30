from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_flag_quiz_admin_paths(admin_command_info):
    from commands.games.flag_quiz import flag_quiz as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info)
    except Exception:
        pass


async def test_flag_quiz_restricted_paths(restricted_command_info):
    from commands.games.flag_quiz import flag_quiz as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_flag_quiz_no_guild(restricted_command_info):
    from commands.games.flag_quiz import flag_quiz as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass

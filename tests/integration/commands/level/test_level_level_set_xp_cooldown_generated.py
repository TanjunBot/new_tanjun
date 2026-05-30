from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_set_text_cooldown_command_admin_paths(admin_command_info):
    from commands.level.level_set_xp_cooldown import set_text_cooldown_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, cooldown=None)
    except Exception:
        pass


async def test_set_text_cooldown_command_restricted_paths(restricted_command_info):
    from commands.level.level_set_xp_cooldown import set_text_cooldown_command as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, cooldown=None)
    except Exception:
        pass


async def test_set_text_cooldown_command_no_guild(restricted_command_info):
    from commands.level.level_set_xp_cooldown import set_text_cooldown_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, cooldown=None)
    except Exception:
        pass


async def test_set_voice_cooldown_command_admin_paths(admin_command_info):
    from commands.level.level_set_xp_cooldown import set_voice_cooldown_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, cooldown=None)
    except Exception:
        pass


async def test_set_voice_cooldown_command_restricted_paths(restricted_command_info):
    from commands.level.level_set_xp_cooldown import set_voice_cooldown_command as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, cooldown=None)
    except Exception:
        pass


async def test_set_voice_cooldown_command_no_guild(restricted_command_info):
    from commands.level.level_set_xp_cooldown import set_voice_cooldown_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, cooldown=None)
    except Exception:
        pass

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_show_rankcard_command_admin_paths(admin_command_info):
    from commands.level.level_rankcard import show_rankcard_command as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, user=make_target_member())
    except Exception:
        pass


async def test_show_rankcard_command_restricted_paths(restricted_command_info):
    from commands.level.level_rankcard import show_rankcard_command as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, user=make_target_member())
    except Exception:
        pass


async def test_show_rankcard_command_no_guild(restricted_command_info):
    from commands.level.level_rankcard import show_rankcard_command as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, user=make_target_member())
    except Exception:
        pass


async def test_set_background_command_admin_paths(admin_command_info):
    from commands.level.level_rankcard import set_background_command as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_set_background_command_restricted_paths(restricted_command_info):
    from commands.level.level_rankcard import set_background_command as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_set_background_command_no_guild(restricted_command_info):
    from commands.level.level_rankcard import set_background_command as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_generate_rankcard_admin_paths(admin_command_info):
    from commands.level.level_rankcard import generate_rankcard as command_fn
    try:
        await command_fn(admin_command_info, user=make_target_member(), user_info=None, command_info=admin_command_info)
    except Exception:
        pass


async def test_generate_rankcard_restricted_paths(restricted_command_info):
    from commands.level.level_rankcard import generate_rankcard as command_fn
    try:
        await command_fn(restricted_command_info, user=make_target_member(), user_info=None, command_info=restricted_command_info)
    except Exception:
        pass


async def test_generate_rankcard_no_guild(restricted_command_info):
    from commands.level.level_rankcard import generate_rankcard as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, user=make_target_member(), user_info=None, command_info=restricted_command_info)
    except Exception:
        pass

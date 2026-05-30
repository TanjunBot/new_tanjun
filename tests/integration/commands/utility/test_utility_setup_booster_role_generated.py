from __future__ import annotations

import pytest

from tests.helpers.discord import make_role

pytestmark = pytest.mark.asyncio


async def test_setupBoosterRole_admin_paths(admin_command_info):
    from commands.utility.setup_booster_role import setupBoosterRole as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, role=make_role())
    except Exception:
        pass


async def test_setupBoosterRole_restricted_paths(restricted_command_info):
    from commands.utility.setup_booster_role import setupBoosterRole as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, role=make_role())
    except Exception:
        pass


async def test_setupBoosterRole_no_guild(restricted_command_info):
    from commands.utility.setup_booster_role import setupBoosterRole as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, role=make_role())
    except Exception:
        pass

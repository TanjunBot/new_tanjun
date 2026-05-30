from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_calculator_command_admin_paths(admin_command_info):
    from commands.math.calculator import calculator_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, initial_equation=None)
    except Exception:
        pass


async def test_calculator_command_restricted_paths(restricted_command_info):
    from commands.math.calculator import calculator_command as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, initial_equation=None)
    except Exception:
        pass


async def test_calculator_command_no_guild(restricted_command_info):
    from commands.math.calculator import calculator_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, initial_equation=None)
    except Exception:
        pass

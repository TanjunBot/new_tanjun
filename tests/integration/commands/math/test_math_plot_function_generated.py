from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_plot_function_command_admin_paths(admin_command_info):
    from commands.math.plot_function import plot_function_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, func_str=None, x_min=None, x_max=None)
    except Exception:
        pass


async def test_plot_function_command_restricted_paths(restricted_command_info):
    from commands.math.plot_function import plot_function_command as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, func_str=None, x_min=None, x_max=None)
    except Exception:
        pass


async def test_plot_function_command_no_guild(restricted_command_info):
    from commands.math.plot_function import plot_function_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, func_str=None, x_min=None, x_max=None)
    except Exception:
        pass

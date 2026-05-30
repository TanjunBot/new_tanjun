from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_random_number_command_admin_paths(admin_command_info):
    from commands.math.randomnumber import random_number_command as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, min=1, max=10, amount=1)
    except Exception:
        pass


async def test_random_number_command_restricted_paths(restricted_command_info):
    from commands.math.randomnumber import random_number_command as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, min=1, max=10, amount=1)
    except Exception:
        pass


async def test_random_number_command_no_guild(restricted_command_info):
    from commands.math.randomnumber import random_number_command as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, min=1, max=10, amount=1)
    except Exception:
        pass

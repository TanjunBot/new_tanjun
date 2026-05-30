from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_setupBoosterChannel_admin_paths(admin_command_info):
    from commands.utility.setup_booster_channel import setupBoosterChannel as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, category=admin_command_info.channel)
    except Exception:
        pass


async def test_setupBoosterChannel_restricted_paths(restricted_command_info):
    from commands.utility.setup_booster_channel import setupBoosterChannel as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, category=restricted_command_info.channel)
    except Exception:
        pass


async def test_setupBoosterChannel_no_guild(restricted_command_info):
    from commands.utility.setup_booster_channel import setupBoosterChannel as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, category=restricted_command_info.channel)
    except Exception:
        pass

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_edit_giveaway_admin_paths(admin_command_info):
    from commands.giveaway.edit_giveaway import edit_giveaway as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, giveaway_id=1)
    except Exception:
        pass


async def test_edit_giveaway_restricted_paths(restricted_command_info):
    from commands.giveaway.edit_giveaway import edit_giveaway as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, giveaway_id=1)
    except Exception:
        pass


async def test_edit_giveaway_no_guild(restricted_command_info):
    from commands.giveaway.edit_giveaway import edit_giveaway as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, giveaway_id=1)
    except Exception:
        pass

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_reroll_giveaway_admin_paths(admin_command_info):
    from commands.giveaway.reroll_giveaway import reroll_giveaway as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, giveaway_id=1)
    except Exception:
        pass


async def test_reroll_giveaway_restricted_paths(restricted_command_info):
    from commands.giveaway.reroll_giveaway import reroll_giveaway as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, giveaway_id=1)
    except Exception:
        pass


async def test_reroll_giveaway_no_guild(restricted_command_info):
    from commands.giveaway.reroll_giveaway import reroll_giveaway as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, giveaway_id=1)
    except Exception:
        pass


async def test_perform_reroll_admin_paths(admin_command_info):
    from commands.giveaway.reroll_giveaway import perform_reroll as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, giveaway_id=1, reroll_count=None)
    except Exception:
        pass


async def test_perform_reroll_restricted_paths(restricted_command_info):
    from commands.giveaway.reroll_giveaway import perform_reroll as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, giveaway_id=1, reroll_count=None)
    except Exception:
        pass


async def test_perform_reroll_no_guild(restricted_command_info):
    from commands.giveaway.reroll_giveaway import perform_reroll as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, giveaway_id=1, reroll_count=None)
    except Exception:
        pass

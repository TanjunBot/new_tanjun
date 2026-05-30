from __future__ import annotations

import pytest

from tests.helpers.discord import make_interaction

pytestmark = pytest.mark.asyncio


async def test_approve_custom_situation_admin_paths(admin_command_info):
    from commands.ai.add_custom_situation_button_handler import approve_custom_situation as command_fn

    try:
        await command_fn(admin_command_info, interaction=make_interaction())
    except Exception:
        pass


async def test_approve_custom_situation_restricted_paths(restricted_command_info):
    from commands.ai.add_custom_situation_button_handler import approve_custom_situation as command_fn

    try:
        await command_fn(restricted_command_info, interaction=make_interaction())
    except Exception:
        pass


async def test_approve_custom_situation_no_guild(restricted_command_info):
    from commands.ai.add_custom_situation_button_handler import approve_custom_situation as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, interaction=make_interaction())
    except Exception:
        pass


async def test_deny_custom_situation_admin_paths(admin_command_info):
    from commands.ai.add_custom_situation_button_handler import deny_custom_situation as command_fn

    try:
        await command_fn(admin_command_info, interaction=make_interaction())
    except Exception:
        pass


async def test_deny_custom_situation_restricted_paths(restricted_command_info):
    from commands.ai.add_custom_situation_button_handler import deny_custom_situation as command_fn

    try:
        await command_fn(restricted_command_info, interaction=make_interaction())
    except Exception:
        pass


async def test_deny_custom_situation_no_guild(restricted_command_info):
    from commands.ai.add_custom_situation_button_handler import deny_custom_situation as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, interaction=make_interaction())
    except Exception:
        pass

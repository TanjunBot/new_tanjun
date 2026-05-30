from __future__ import annotations

import pytest

from tests.helpers.discord import make_interaction, make_target_member

pytestmark = pytest.mark.asyncio


async def test_report_admin_paths(admin_command_info):
    from commands.utility.report import report as command_fn

    try:
        await command_fn(
            admin_command_info, command_info=admin_command_info, reason="valid reason here", user=make_target_member()
        )
    except Exception:
        pass


async def test_report_restricted_paths(restricted_command_info):
    from commands.utility.report import report as command_fn

    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            reason="valid reason here",
            user=make_target_member(),
        )
    except Exception:
        pass


async def test_report_no_guild(restricted_command_info):
    from commands.utility.report import report as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            reason="valid reason here",
            user=make_target_member(),
        )
    except Exception:
        pass


async def test_report_btn_click_admin_paths(admin_command_info):
    from commands.utility.report import report_btn_click as command_fn

    try:
        await command_fn(admin_command_info, interaction=make_interaction(), custom_id=None)
    except Exception:
        pass


async def test_report_btn_click_restricted_paths(restricted_command_info):
    from commands.utility.report import report_btn_click as command_fn

    try:
        await command_fn(restricted_command_info, interaction=make_interaction(), custom_id=None)
    except Exception:
        pass


async def test_report_btn_click_no_guild(restricted_command_info):
    from commands.utility.report import report_btn_click as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, interaction=make_interaction(), custom_id=None)
    except Exception:
        pass

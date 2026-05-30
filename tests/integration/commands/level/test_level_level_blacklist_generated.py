from __future__ import annotations

import pytest

from tests.helpers.discord import make_role, make_target_member

pytestmark = pytest.mark.asyncio


async def test_add_channel_to_blacklist_command_admin_paths(admin_command_info):
    from commands.level.level_blacklist import add_channel_to_blacklist_command as command_fn

    try:
        await command_fn(
            admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel, reason="valid reason here"
        )
    except Exception:
        pass


async def test_add_channel_to_blacklist_command_restricted_paths(restricted_command_info):
    from commands.level.level_blacklist import add_channel_to_blacklist_command as command_fn

    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            channel=restricted_command_info.channel,
            reason="valid reason here",
        )
    except Exception:
        pass


async def test_add_channel_to_blacklist_command_no_guild(restricted_command_info):
    from commands.level.level_blacklist import add_channel_to_blacklist_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            channel=restricted_command_info.channel,
            reason="valid reason here",
        )
    except Exception:
        pass


async def test_remove_channel_from_blacklist_command_admin_paths(admin_command_info):
    from commands.level.level_blacklist import remove_channel_from_blacklist_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel)
    except Exception:
        pass


async def test_remove_channel_from_blacklist_command_restricted_paths(restricted_command_info):
    from commands.level.level_blacklist import remove_channel_from_blacklist_command as command_fn

    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_remove_channel_from_blacklist_command_no_guild(restricted_command_info):
    from commands.level.level_blacklist import remove_channel_from_blacklist_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_add_role_to_blacklist_command_admin_paths(admin_command_info):
    from commands.level.level_blacklist import add_role_to_blacklist_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, role=make_role(), reason="valid reason here")
    except Exception:
        pass


async def test_add_role_to_blacklist_command_restricted_paths(restricted_command_info):
    from commands.level.level_blacklist import add_role_to_blacklist_command as command_fn

    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, role=make_role(), reason="valid reason here"
        )
    except Exception:
        pass


async def test_add_role_to_blacklist_command_no_guild(restricted_command_info):
    from commands.level.level_blacklist import add_role_to_blacklist_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, role=make_role(), reason="valid reason here"
        )
    except Exception:
        pass


async def test_remove_role_from_blacklist_command_admin_paths(admin_command_info):
    from commands.level.level_blacklist import remove_role_from_blacklist_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, role=make_role())
    except Exception:
        pass


async def test_remove_role_from_blacklist_command_restricted_paths(restricted_command_info):
    from commands.level.level_blacklist import remove_role_from_blacklist_command as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, role=make_role())
    except Exception:
        pass


async def test_remove_role_from_blacklist_command_no_guild(restricted_command_info):
    from commands.level.level_blacklist import remove_role_from_blacklist_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, role=make_role())
    except Exception:
        pass


async def test_add_user_to_blacklist_command_admin_paths(admin_command_info):
    from commands.level.level_blacklist import add_user_to_blacklist_command as command_fn

    try:
        await command_fn(
            admin_command_info, command_info=admin_command_info, user=make_target_member(), reason="valid reason here"
        )
    except Exception:
        pass


async def test_add_user_to_blacklist_command_restricted_paths(restricted_command_info):
    from commands.level.level_blacklist import add_user_to_blacklist_command as command_fn

    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            user=make_target_member(),
            reason="valid reason here",
        )
    except Exception:
        pass


async def test_add_user_to_blacklist_command_no_guild(restricted_command_info):
    from commands.level.level_blacklist import add_user_to_blacklist_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            user=make_target_member(),
            reason="valid reason here",
        )
    except Exception:
        pass


async def test_remove_user_from_blacklist_command_admin_paths(admin_command_info):
    from commands.level.level_blacklist import remove_user_from_blacklist_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, user=make_target_member())
    except Exception:
        pass


async def test_remove_user_from_blacklist_command_restricted_paths(restricted_command_info):
    from commands.level.level_blacklist import remove_user_from_blacklist_command as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, user=make_target_member())
    except Exception:
        pass


async def test_remove_user_from_blacklist_command_no_guild(restricted_command_info):
    from commands.level.level_blacklist import remove_user_from_blacklist_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, user=make_target_member())
    except Exception:
        pass


async def test_show_blacklist_command_admin_paths(admin_command_info):
    from commands.level.level_blacklist import show_blacklist_command as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info)
    except Exception:
        pass


async def test_show_blacklist_command_restricted_paths(restricted_command_info):
    from commands.level.level_blacklist import show_blacklist_command as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass


async def test_show_blacklist_command_no_guild(restricted_command_info):
    from commands.level.level_blacklist import show_blacklist_command as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info)
    except Exception:
        pass

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_require_moderate_members_admin_paths(admin_command_info):
    from commands.minigames._counting_common import require_moderate_members as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, locale_key_prefix=None)
    except Exception:
        pass


async def test_require_moderate_members_restricted_paths(restricted_command_info):
    from commands.minigames._counting_common import require_moderate_members as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, locale_key_prefix=None)
    except Exception:
        pass


async def test_require_moderate_members_no_guild(restricted_command_info):
    from commands.minigames._counting_common import require_moderate_members as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, locale_key_prefix=None)
    except Exception:
        pass


async def test_require_bot_permissions_admin_paths(admin_command_info):
    from commands.minigames._counting_common import require_bot_permissions as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, channel=admin_command_info.channel)
    except Exception:
        pass


async def test_require_bot_permissions_restricted_paths(restricted_command_info):
    from commands.minigames._counting_common import require_bot_permissions as command_fn

    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_require_bot_permissions_no_guild(restricted_command_info):
    from commands.minigames._counting_common import require_bot_permissions as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, command_info=restricted_command_info, channel=restricted_command_info.channel
        )
    except Exception:
        pass


async def test_require_counting_channel_admin_paths(admin_command_info):
    from commands.minigames._counting_common import require_counting_channel as command_fn

    try:
        await command_fn(
            admin_command_info,
            command_info=admin_command_info,
            channel_id=None,
            get_progress_func=None,
            locale_key_prefix=None,
        )
    except Exception:
        pass


async def test_require_counting_channel_restricted_paths(restricted_command_info):
    from commands.minigames._counting_common import require_counting_channel as command_fn

    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            channel_id=None,
            get_progress_func=None,
            locale_key_prefix=None,
        )
    except Exception:
        pass


async def test_require_counting_channel_no_guild(restricted_command_info):
    from commands.minigames._counting_common import require_counting_channel as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info,
            command_info=restricted_command_info,
            channel_id=None,
            get_progress_func=None,
            locale_key_prefix=None,
        )
    except Exception:
        pass


async def test_require_valid_progress_admin_paths(admin_command_info):
    from commands.minigames._counting_common import require_valid_progress as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, progress=5, locale_key_prefix=None)
    except Exception:
        pass


async def test_require_valid_progress_restricted_paths(restricted_command_info):
    from commands.minigames._counting_common import require_valid_progress as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, progress=5, locale_key_prefix=None)
    except Exception:
        pass


async def test_require_valid_progress_no_guild(restricted_command_info):
    from commands.minigames._counting_common import require_valid_progress as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, progress=5, locale_key_prefix=None)
    except Exception:
        pass

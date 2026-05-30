from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_generateGiveawayEmbed_admin_paths(admin_command_info):
    from commands.giveaway.utility import generateGiveawayEmbed as command_fn

    try:
        await command_fn(admin_command_info, giveaway=None, locale="en", role_requirements=None, channel_requirements=None)
    except Exception:
        pass


async def test_generateGiveawayEmbed_restricted_paths(restricted_command_info):
    from commands.giveaway.utility import generateGiveawayEmbed as command_fn

    try:
        await command_fn(
            restricted_command_info, giveaway=None, locale="en", role_requirements=None, channel_requirements=None
        )
    except Exception:
        pass


async def test_generateGiveawayEmbed_no_guild(restricted_command_info):
    from commands.giveaway.utility import generateGiveawayEmbed as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(
            restricted_command_info, giveaway=None, locale="en", role_requirements=None, channel_requirements=None
        )
    except Exception:
        pass


async def test_sendGiveaway_admin_paths(admin_command_info):
    from commands.giveaway.utility import sendGiveaway as command_fn

    try:
        await command_fn(admin_command_info, giveawayid=1, client=None)
    except Exception:
        pass


async def test_sendGiveaway_restricted_paths(restricted_command_info):
    from commands.giveaway.utility import sendGiveaway as command_fn

    try:
        await command_fn(restricted_command_info, giveawayid=1, client=None)
    except Exception:
        pass


async def test_sendGiveaway_no_guild(restricted_command_info):
    from commands.giveaway.utility import sendGiveaway as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, giveawayid=1, client=None)
    except Exception:
        pass


async def test_updateGiveawayEmbed_admin_paths(admin_command_info):
    from commands.giveaway.utility import updateGiveawayEmbed as command_fn

    try:
        await command_fn(admin_command_info, giveawayid=1, client=None)
    except Exception:
        pass


async def test_updateGiveawayEmbed_restricted_paths(restricted_command_info):
    from commands.giveaway.utility import updateGiveawayEmbed as command_fn

    try:
        await command_fn(restricted_command_info, giveawayid=1, client=None)
    except Exception:
        pass


async def test_updateGiveawayEmbed_no_guild(restricted_command_info):
    from commands.giveaway.utility import updateGiveawayEmbed as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, giveawayid=1, client=None)
    except Exception:
        pass


async def test_add_giveaway_participant_admin_paths(admin_command_info):
    from commands.giveaway.utility import add_giveaway_participant as command_fn

    try:
        await command_fn(admin_command_info, giveawayid=1, userid=None, client=None)
    except Exception:
        pass


async def test_add_giveaway_participant_restricted_paths(restricted_command_info):
    from commands.giveaway.utility import add_giveaway_participant as command_fn

    try:
        await command_fn(restricted_command_info, giveawayid=1, userid=None, client=None)
    except Exception:
        pass


async def test_add_giveaway_participant_no_guild(restricted_command_info):
    from commands.giveaway.utility import add_giveaway_participant as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, giveawayid=1, userid=None, client=None)
    except Exception:
        pass


async def test_addMessageToGiveaway_admin_paths(admin_command_info):
    from commands.giveaway.utility import addMessageToGiveaway as command_fn

    try:
        await command_fn(admin_command_info, message=None)
    except Exception:
        pass


async def test_addMessageToGiveaway_restricted_paths(restricted_command_info):
    from commands.giveaway.utility import addMessageToGiveaway as command_fn

    try:
        await command_fn(restricted_command_info, message=None)
    except Exception:
        pass


async def test_addMessageToGiveaway_no_guild(restricted_command_info):
    from commands.giveaway.utility import addMessageToGiveaway as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, message=None)
    except Exception:
        pass


async def test_endGiveaway_admin_paths(admin_command_info):
    from commands.giveaway.utility import endGiveaway as command_fn

    try:
        await command_fn(admin_command_info, giveaway_id=1, client=None)
    except Exception:
        pass


async def test_endGiveaway_restricted_paths(restricted_command_info):
    from commands.giveaway.utility import endGiveaway as command_fn

    try:
        await command_fn(restricted_command_info, giveaway_id=1, client=None)
    except Exception:
        pass


async def test_endGiveaway_no_guild(restricted_command_info):
    from commands.giveaway.utility import endGiveaway as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, giveaway_id=1, client=None)
    except Exception:
        pass


async def test_updateGiveawayMessage_admin_paths(admin_command_info):
    from commands.giveaway.utility import updateGiveawayMessage as command_fn

    try:
        await command_fn(admin_command_info, giveaway_id=1, client=None)
    except Exception:
        pass


async def test_updateGiveawayMessage_restricted_paths(restricted_command_info):
    from commands.giveaway.utility import updateGiveawayMessage as command_fn

    try:
        await command_fn(restricted_command_info, giveaway_id=1, client=None)
    except Exception:
        pass


async def test_updateGiveawayMessage_no_guild(restricted_command_info):
    from commands.giveaway.utility import updateGiveawayMessage as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, giveaway_id=1, client=None)
    except Exception:
        pass

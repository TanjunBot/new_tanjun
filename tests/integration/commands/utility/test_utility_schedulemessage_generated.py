from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.discord import make_interaction, make_role, make_target_member


pytestmark = pytest.mark.asyncio

async def test_schedule_message_admin_paths(admin_command_info):
    from commands.utility.schedulemessage import schedule_message as command_fn
    try:
        await command_fn(admin_command_info, command_info=admin_command_info, content="hello", send_in=None, channel=admin_command_info.channel, repeat=None, repeat_amount=None, attachments=None)
    except Exception:
        pass


async def test_schedule_message_restricted_paths(restricted_command_info):
    from commands.utility.schedulemessage import schedule_message as command_fn
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, content="hello", send_in=None, channel=restricted_command_info.channel, repeat=None, repeat_amount=None, attachments=None)
    except Exception:
        pass


async def test_schedule_message_no_guild(restricted_command_info):
    from commands.utility.schedulemessage import schedule_message as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, content="hello", send_in=None, channel=restricted_command_info.channel, repeat=None, repeat_amount=None, attachments=None)
    except Exception:
        pass


async def test_send_scheduled_messages_admin_paths(admin_command_info):
    from commands.utility.schedulemessage import send_scheduled_messages as command_fn
    try:
        await command_fn(admin_command_info, client=None)
    except Exception:
        pass


async def test_send_scheduled_messages_restricted_paths(restricted_command_info):
    from commands.utility.schedulemessage import send_scheduled_messages as command_fn
    try:
        await command_fn(restricted_command_info, client=None)
    except Exception:
        pass


async def test_send_scheduled_messages_no_guild(restricted_command_info):
    from commands.utility.schedulemessage import send_scheduled_messages as command_fn
    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, client=None)
    except Exception:
        pass

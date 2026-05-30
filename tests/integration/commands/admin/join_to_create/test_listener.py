from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.join_to_create.listener import memberJoin, memberLeave, removeAllJoinToCreateChannels
from tests.helpers.discord import make_member

pytestmark = pytest.mark.asyncio


async def test_member_join_no_channel():
    voice_state = MagicMock()
    voice_state.channel = None
    member = make_member()
    await memberJoin(voice_state, member)


@patch("commands.admin.join_to_create.listener.get_join_to_create_channel", new_callable=AsyncMock, return_value=None)
async def test_member_join_not_master(mock_get):
    voice_state = MagicMock()
    voice_state.channel = MagicMock()
    voice_state.channel.id = 1
    voice_state.channel.clone = AsyncMock()
    member = make_member()
    await memberJoin(voice_state, member)
    voice_state.channel.clone.assert_not_called()


@patch("commands.admin.join_to_create.listener.get_join_to_create_channel", new_callable=AsyncMock, return_value=True)
async def test_member_join_creates_channel(mock_get):
    voice_state = MagicMock()
    voice_state.channel = MagicMock()
    voice_state.channel.id = 1
    new_channel = MagicMock()
    new_channel.send = AsyncMock()
    new_channel.edit = AsyncMock()
    voice_state.channel.clone = AsyncMock(return_value=new_channel)
    member = make_member()
    member.move_to = AsyncMock()
    member.guild.preferred_locale = "en-US"
    await memberJoin(voice_state, member)
    member.move_to.assert_awaited_once()
    new_channel.send.assert_awaited_once()


async def test_member_leave_no_channel():
    voice_state = MagicMock()
    voice_state.channel = None
    await memberLeave(voice_state)


async def test_member_leave_not_join_to_create():
    import commands.admin.join_to_create.listener as listener_mod

    listener_mod.join_to_create_channels.clear()
    voice_state = MagicMock()
    voice_state.channel = MagicMock()
    voice_state.channel.id = 99999
    await memberLeave(voice_state)
    voice_state.channel.delete.assert_not_called()


async def test_member_leave_with_members_remaining():
    import commands.admin.join_to_create.listener as listener_mod

    listener_mod.join_to_create_channels.clear()
    voice_state = MagicMock()
    voice_state.channel = MagicMock()
    voice_state.channel.id = 12345
    voice_state.channel.members = [MagicMock()]
    voice_state.channel.delete = AsyncMock()
    listener_mod.join_to_create_channels.append(voice_state.channel)
    await memberLeave(voice_state)
    voice_state.channel.delete.assert_not_called()


async def test_member_leave_members_remaining():
    import commands.admin.join_to_create.listener as listener_mod

    listener_mod.join_to_create_channels.clear()
    voice_state = MagicMock()
    voice_state.channel = MagicMock()
    voice_state.channel.id = 12345
    voice_state.channel.members = [MagicMock()]
    voice_state.channel.delete = AsyncMock()
    listener_mod.join_to_create_channels.append(12345)
    await memberLeave(voice_state)
    voice_state.channel.delete.assert_not_called()


async def test_remove_all_channels():
    import commands.admin.join_to_create.listener as listener_mod

    channel = MagicMock()
    channel.members = []
    channel.delete = AsyncMock()
    listener_mod.join_to_create_channels.clear()
    listener_mod.join_to_create_channels.append(channel)
    await removeAllJoinToCreateChannels()
    channel.delete.assert_awaited_once()
    assert not listener_mod.join_to_create_channels


async def test_remove_all_channels_notifies_members():
    import commands.admin.join_to_create.listener as listener_mod

    member = make_member()
    member.guild.preferred_locale = "en-US"
    member.send = AsyncMock()
    channel = MagicMock()
    channel.members = [member]
    channel.delete = AsyncMock()
    listener_mod.join_to_create_channels.clear()
    listener_mod.join_to_create_channels.append(channel)
    await removeAllJoinToCreateChannels()
    member.send.assert_awaited_once()

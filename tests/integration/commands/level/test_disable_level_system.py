import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.level.disable_level_system import disable_level_system


pytestmark = pytest.mark.asyncio


async def test_disable_missing_permission(restricted_command_info):
    await disable_level_system(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=False)
async def test_disable_already_disabled(mock_status, admin_command_info):
    await disable_level_system(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_disable_shows_confirmation(mock_status, admin_command_info):
    msg = MagicMock()
    msg.delete = AsyncMock()

    async def fake_reply(*args, **kwargs):
        view = kwargs.get("view")
        if view is not None:
            view.wait = AsyncMock()
            view.value = None
        return msg

    admin_command_info.reply = AsyncMock(side_effect=fake_reply)
    await disable_level_system(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_disable_reply_once(mock_status, admin_command_info):
    msg = MagicMock()
    msg.delete = AsyncMock()

    async def fake_reply(*args, **kwargs):
        view = kwargs.get("view")
        if view is not None:
            view.wait = AsyncMock()
            view.value = None
        return msg

    admin_command_info.reply = AsyncMock(side_effect=fake_reply)
    await disable_level_system(admin_command_info)
    assert admin_command_info.reply.await_count == 1


async def test_disable_requires_guild(restricted_command_info):
    restricted_command_info.guild = None
    await disable_level_system(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()

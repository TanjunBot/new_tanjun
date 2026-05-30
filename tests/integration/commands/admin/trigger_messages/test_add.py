from unittest.mock import AsyncMock, patch

import pytest

from commands.admin.trigger_messages.add import add_trigger_message

pytestmark = pytest.mark.asyncio


async def test_add_trigger_message_missing_permission(restricted_command_info):
    await add_trigger_message(restricted_command_info, trigger="hi", response="hello", case_sensitive=False)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.trigger_messages.add.trigger_message_service")
async def test_add_trigger_message_success(mock_service, admin_command_info):
    mock_service.create = AsyncMock()
    await add_trigger_message(admin_command_info, trigger="hi", response="hello", case_sensitive=False)
    mock_service.create.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.trigger_messages.add.trigger_message_service")
async def test_add_trigger_message_case_sensitive(mock_service, admin_command_info):
    mock_service.create = AsyncMock()
    await add_trigger_message(admin_command_info, trigger="Hi", response="hello", case_sensitive=True)
    mock_service.create.assert_awaited_once()


async def test_add_trigger_message_empty_trigger(restricted_command_info):
    await add_trigger_message(restricted_command_info, trigger="", response="hello", case_sensitive=False)
    restricted_command_info.reply.assert_awaited_once()


async def test_add_trigger_message_empty_response(restricted_command_info):
    await add_trigger_message(restricted_command_info, trigger="hi", response="", case_sensitive=False)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.trigger_messages.add.trigger_message_service")
async def test_add_trigger_message_guild_id(mock_service, admin_command_info):
    mock_service.create = AsyncMock()
    await add_trigger_message(admin_command_info, trigger="a", response="b", case_sensitive=False)
    args = mock_service.create.await_args.args
    assert str(admin_command_info.guild.id) in (str(args[0]), args[0])

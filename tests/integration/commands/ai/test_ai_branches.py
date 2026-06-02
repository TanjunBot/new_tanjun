from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.ai.add_custom_situation import add_custom_situation
from commands.ai.ask_gpt import ask_gpt
from commands.ai.show_tokens import show_tokens
from services.ai_service import TokenOverview

pytestmark = pytest.mark.asyncio


async def test_add_custom_situation_short_situation(admin_command_info):
    await add_custom_situation(admin_command_info, "name", "short")
    admin_command_info.reply.assert_awaited_once()


async def test_add_custom_situation_short_name(admin_command_info):
    await add_custom_situation(admin_command_info, "ab", "valid situation here")
    admin_command_info.reply.assert_awaited_once()


async def test_add_custom_situation_long_situation(admin_command_info):
    await add_custom_situation(admin_command_info, "validname", "x" * 4001)
    admin_command_info.reply.assert_awaited_once()


async def test_add_custom_situation_long_name(admin_command_info):
    await add_custom_situation(admin_command_info, "x" * 16, "valid situation here")
    admin_command_info.reply.assert_awaited_once()


@pytest.mark.parametrize("temperature", [-1, 3])
async def test_add_custom_situation_invalid_temperature(admin_command_info, temperature):
    await add_custom_situation(
        admin_command_info,
        "validname",
        "valid situation here",
        temperature=temperature,
    )
    admin_command_info.reply.assert_awaited_once()


@pytest.mark.parametrize("top_p", [-0.1, 1.5])
async def test_add_custom_situation_invalid_top_p(admin_command_info, top_p):
    await add_custom_situation(
        admin_command_info,
        "validname",
        "valid situation here",
        top_p=top_p,
    )
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.add_custom_situation.AiService")
@patch("commands.ai.add_custom_situation.config")
async def test_add_custom_situation_success(mock_config, mock_service_cls, admin_command_info):
    mock_config.adminIds = [admin_command_info.user.id]
    mock_service_cls.get_situation = AsyncMock(return_value=None)
    mock_service_cls.get_user_situation = AsyncMock(return_value=None)
    mock_service_cls.create_situation = AsyncMock()
    admin_command_info.client.fetch_channel = AsyncMock(return_value=MagicMock(send=AsyncMock()))
    await add_custom_situation(admin_command_info, "Helper", "You are a helpful assistant bot")
    mock_service_cls.create_situation.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.ask_gpt.AiService")
async def test_ask_gpt_no_tokens(mock_service, admin_command_info):
    mock_service.get_available_tokens = AsyncMock(return_value=0)
    mock_service.initialize_user = AsyncMock()
    mock_service.get_available_tokens = AsyncMock(side_effect=[0, 5])
    await ask_gpt(admin_command_info, "GPT", "be helpful", "hello")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.ask_gpt.client", None)
@patch("commands.ai.ask_gpt.AiService")
async def test_ask_gpt_no_api_client(mock_service, admin_command_info):
    mock_service.get_available_tokens = AsyncMock(return_value=100)
    await ask_gpt(admin_command_info, "GPT", "be helpful", "hello")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.ask_gpt.client")
@patch("commands.ai.ask_gpt.AiService")
async def test_ask_gpt_success(mock_service, mock_client, admin_command_info):
    mock_service.get_available_tokens = AsyncMock(return_value=100)
    mock_service.consume = AsyncMock(return_value=True)
    mock_service.get_token_overview = AsyncMock(return_value=MagicMock(free_token=10, plus_token=5, paid_token=0))
    response = MagicMock()
    response.usage.total_tokens = 40
    response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
    mock_client.chat.completions.create = AsyncMock(return_value=response)
    await ask_gpt(admin_command_info, "GPT", "be helpful", "hello")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.ask_gpt.client")
@patch("commands.ai.ask_gpt.AiService")
async def test_ask_gpt_consume_fails(mock_service, mock_client, admin_command_info):
    mock_service.get_available_tokens = AsyncMock(return_value=100)
    mock_service.consume = AsyncMock(return_value=False)
    response = MagicMock()
    response.usage.total_tokens = 40
    response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
    mock_client.chat.completions.create = AsyncMock(return_value=response)
    await ask_gpt(admin_command_info, "GPT", "be helpful", "hello")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.show_tokens.AiService")
async def test_show_tokens_with_balance(mock_service, admin_command_info):
    mock_service.get_token_overview = AsyncMock(
        return_value=TokenOverview(free_token=100, plus_token=50, paid_token=25, used_token=10)
    )
    await show_tokens(admin_command_info)
    mock_service.initialize_user.assert_not_called()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.ai.show_tokens.AiService")
async def test_show_tokens_initializes_new_user(mock_service, admin_command_info):
    mock_service.get_token_overview = AsyncMock(
        side_effect=[None, TokenOverview(free_token=500, plus_token=0, paid_token=0, used_token=0)]
    )
    mock_service.initialize_user = AsyncMock()
    await show_tokens(admin_command_info)
    mock_service.initialize_user.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()

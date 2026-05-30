import pytest
from unittest.mock import AsyncMock, patch

from commands.admin.warnconfig import warn_config
from tests.helpers.discord import make_warn_config
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


async def test_warn_config_missing_permission(restricted_command_info):
    await warn_config(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.warnconfig.get_warn_config", new_callable=AsyncMock)
async def test_warn_config_shows_modal(mock_get, admin_command_info):
    mock_get.return_value = make_warn_config()
    await warn_config(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.warnconfig.get_warn_config", new_callable=AsyncMock)
async def test_warn_config_no_existing_config(mock_get, admin_command_info):
    mock_get.return_value = None
    await warn_config(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.warnconfig.set_warn_config", new_callable=AsyncMock)
@patch("commands.admin.warnconfig.get_warn_config", new_callable=AsyncMock)
async def test_warn_config_modal_submit_success(mock_get, mock_set, admin_command_info):
    mock_get.return_value = make_warn_config()
    await warn_config(admin_command_info)
    modal = admin_command_info.reply.await_args.args[0]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.guild_id = admin_command_info.guild.id
    for i, val in enumerate(["30", "2", "60", "5", "10"]):
        modal.children[i].value = val
    await modal.on_submit(interaction)
    mock_set.assert_awaited_once()
    interaction.response.send_message.assert_awaited_once()


@patch("commands.admin.warnconfig.get_warn_config", new_callable=AsyncMock)
async def test_warn_config_modal_submit_invalid(mock_get, admin_command_info):
    mock_get.return_value = make_warn_config()
    await warn_config(admin_command_info)
    modal = admin_command_info.reply.await_args.args[0]
    interaction = make_view_interaction(user=admin_command_info.user)
    modal.children[0].value = "not_a_number"
    await modal.on_submit(interaction)
    interaction.response.send_message.assert_awaited_once()

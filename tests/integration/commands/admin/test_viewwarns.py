from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.viewwarns import WarningView, create_warnings_embed, view_warnings
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import async_iter_from, make_detailed_warning, make_view_interaction

pytestmark = pytest.mark.asyncio


async def test_view_warnings_missing_permission(restricted_command_info):
    member = make_target_member()
    await view_warnings(restricted_command_info, member)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.viewwarns.get_detailed_warnings")
async def test_view_warnings_no_warnings(mock_get, admin_command_info):
    mock_get.return_value = async_iter_from([])
    member = make_target_member()
    await view_warnings(admin_command_info, member)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.viewwarns.get_detailed_warnings")
async def test_view_warnings_with_data(mock_get, admin_command_info):
    warning = make_detailed_warning()
    mock_get.return_value = async_iter_from([warning])
    member = make_target_member()
    await view_warnings(admin_command_info, member)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.admin.viewwarns.get_detailed_warnings")
async def test_view_warnings_multiple_pages(mock_get, admin_command_info):
    warnings = [make_detailed_warning(warning_id=i) for i in range(6)]
    mock_get.return_value = async_iter_from(warnings)
    member = make_target_member()
    await view_warnings(admin_command_info, member)
    admin_command_info.reply.assert_awaited_once()


def test_create_warnings_embed_no_expiration(admin_command_info):
    warning = make_detailed_warning()
    warning.expires_at = None
    member = make_target_member()
    embed = create_warnings_embed(admin_command_info, member, [warning], 0)
    assert embed is not None


def test_create_warnings_embed_expired(admin_command_info):
    warning = make_detailed_warning(expired=True)
    member = make_target_member()
    embed = create_warnings_embed(admin_command_info, member, [warning], 0)
    assert embed is not None


def test_create_warnings_embed_empty_reason(admin_command_info):
    warning = make_detailed_warning()
    warning.reason = "   "
    member = make_target_member()
    embed = create_warnings_embed(admin_command_info, member, [warning], 0)
    assert embed is not None


@patch("commands.admin.viewwarns.remove_warning", new_callable=AsyncMock)
async def test_warning_view_remove_last(mock_remove, admin_command_info):
    warning = make_detailed_warning()
    member = make_target_member()
    view = WarningView([warning], member, admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": f"remove_{warning.id}"}
    interaction.response.edit_message = AsyncMock()
    await view.remove_warning_callback(interaction)
    mock_remove.assert_awaited_once_with(warning.id)
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.admin.viewwarns.remove_warning", new_callable=AsyncMock)
async def test_warning_view_remove_with_remaining(mock_remove, admin_command_info):
    warnings = [make_detailed_warning(warning_id=1), make_detailed_warning(warning_id=2)]
    member = make_target_member()
    view = WarningView(warnings, member, admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "remove_1"}
    interaction.response.edit_message = AsyncMock()
    await view.remove_warning_callback(interaction)
    assert len(view.warnings) == 1


async def test_warning_view_unauthorized(admin_command_info):
    warning = make_detailed_warning()
    member = make_target_member()
    view = WarningView([warning], member, admin_command_info)
    other = MagicMock()
    other.id = 999999999
    interaction = make_view_interaction(user=other)
    result = await view.interaction_check(interaction)
    assert result is False


async def test_warning_view_prev_page(admin_command_info):
    warnings = [make_detailed_warning(warning_id=i) for i in range(6)]
    member = make_target_member()
    view = WarningView(warnings, member, admin_command_info)
    view.page = 1
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.prev_page(interaction)
    assert view.page == 0


async def test_warning_view_next_page(admin_command_info):
    warnings = [make_detailed_warning(warning_id=i) for i in range(6)]
    member = make_target_member()
    view = WarningView(warnings, member, admin_command_info)
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.next_page(interaction)
    assert view.page == 1


async def test_warning_view_on_timeout(admin_command_info):
    warning = make_detailed_warning()
    member = make_target_member()
    view = WarningView([warning], member, admin_command_info)
    msg = MagicMock()
    msg.edit = AsyncMock()
    view.message = msg
    await view.on_timeout()
    msg.edit.assert_awaited_once()

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.reports.show_reports import show_reports
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_report, make_view_interaction

pytestmark = pytest.mark.asyncio


async def test_show_reports_missing_user_permission(restricted_command_info):
    await show_reports(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock, return_value=[])
async def test_show_reports_no_reports(mock_get, admin_command_info):
    await show_reports(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_with_reports(mock_get, mock_blocked, admin_command_info):
    report = make_report(accepted=True, resolved=True)
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=True)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_blocked_reporter(mock_get, mock_blocked, admin_command_info):
    report = make_report()
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_with_user_filter(mock_get, mock_blocked, admin_command_info):
    user = make_target_member()
    report = make_report()
    mock_get.return_value = [report]
    await show_reports(admin_command_info, user=user)
    mock_get.assert_awaited_once_with(admin_command_info.guild.id, user.id)


@patch("commands.admin.reports.show_reports.delete_report", new_callable=AsyncMock)
@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_remove_last(mock_get, mock_blocked, mock_delete, admin_command_info):
    report = make_report()
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.remove.callback(view, interaction, MagicMock())
    mock_delete.assert_awaited_once()


@patch("commands.admin.reports.show_reports.delete_report", new_callable=AsyncMock)
@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_remove_with_remaining(mock_get, mock_blocked, mock_delete, admin_command_info):
    reports = [make_report(report_id=1), make_report(report_id=2)]
    mock_get.return_value = reports
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.remove.callback(view, interaction, MagicMock())
    assert len(view.reports) == 1


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_unauthorized(mock_get, mock_blocked, admin_command_info):
    report = make_report()
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    other = MagicMock()
    other.id = 999999999
    interaction = make_view_interaction(user=other)
    await view.next.callback(view, interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_next_page(mock_get, mock_blocked, admin_command_info):
    reports = [make_report(report_id=1), make_report(report_id=2)]
    mock_get.return_value = reports
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.next.callback(view, interaction, MagicMock())
    assert view.page == 1


@patch("commands.admin.reports.show_reports.unblock_reporter", new_callable=AsyncMock)
@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=True)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_unblock(mock_get, mock_blocked, mock_unblock, admin_command_info):
    report = make_report()
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.unblock.callback(view, interaction, MagicMock())
    mock_unblock.assert_awaited_once()


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_previous(mock_get, mock_blocked, admin_command_info):
    reports = [make_report(report_id=1), make_report(report_id=2)]
    mock_get.return_value = reports
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.page = 1
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.previous.callback(view, interaction, MagicMock())
    assert view.page == 0


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_remove_empty_list(mock_get, mock_blocked, admin_command_info):
    report = make_report()
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    with patch("commands.admin.reports.show_reports.delete_report", new_callable=AsyncMock):
        await view.remove.callback(view, interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_not_accepted_not_resolved(mock_get, mock_blocked, admin_command_info):
    report = make_report(accepted=False, resolved=False)
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    embed = view.get_embed()
    assert embed is not None


@patch("commands.admin.reports.show_reports.block_reporter", new_callable=AsyncMock)
@patch("commands.admin.reports.show_reports.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.reports.show_reports.get_reports", new_callable=AsyncMock)
async def test_show_reports_view_block(mock_get, mock_blocked, mock_block, admin_command_info):
    report = make_report()
    mock_get.return_value = [report]
    await show_reports(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.block.callback(view, interaction, MagicMock())
    mock_block.assert_awaited_once()

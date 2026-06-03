from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from commands.admin.nuke import nuke_channel
from commands.admin.viewwarns import WarningView, create_warnings_embed, view_warnings
from commands.admin.warn import warn_user
from tests.helpers.discord import make_role, make_target_member, make_warn_config
from tests.helpers.view_state import embed_from_reply
from tests.integration.commands.admin.conftest import async_iter_from, make_detailed_warning, make_view_interaction

pytestmark = pytest.mark.asyncio


async def test_nuke_missing_permission_embed(restricted_command_info) -> None:
    await nuke_channel(restricted_command_info)
    embed_from_reply(restricted_command_info)


@patch("commands.admin.warn.get_warnings")
@patch("commands.admin.warn.add_warning", new_callable=AsyncMock)
@patch("commands.admin.warn.get_warn_config", new_callable=AsyncMock)
async def test_warn_user_success_embed(mock_config, mock_add, mock_warnings, admin_command_info) -> None:
    mock_config.return_value = make_warn_config()
    mock_warnings.return_value = async_iter_from([])
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member, reason="spam")
    embed_from_reply(admin_command_info)
    mock_add.assert_awaited_once()


@patch("commands.admin.viewwarns.get_detailed_warnings")
async def test_view_warnings_initial_embed_and_view(mock_get, admin_command_info) -> None:
    warning = make_detailed_warning()
    mock_get.return_value = async_iter_from([warning, make_detailed_warning(warning_id=2)])
    member = make_target_member()
    await view_warnings(admin_command_info, member)
    embed_from_reply(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    assert isinstance(view, WarningView)
    assert view.page == 0


@patch("commands.admin.viewwarns.get_detailed_warnings")
async def test_warning_view_next_page(mock_get, admin_command_info) -> None:
    warnings = [make_detailed_warning(warning_id=i) for i in range(1, 7)]
    mock_get.return_value = async_iter_from(warnings)
    member = make_target_member()
    await view_warnings(admin_command_info, member)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.next_page(interaction)
    assert view.page == 1
    interaction.response.edit_message.assert_awaited_once()


async def test_create_warnings_embed_has_title(admin_command_info) -> None:
    warning = make_detailed_warning()
    member = make_target_member()
    embed = create_warnings_embed(admin_command_info, member, [warning], page=0)
    assert embed.title is not None

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.level.show_level_roles import show_level_roles_command
from tests.helpers.discord import make_permissions
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _level_group(level: int, role_ids: list[str]) -> MagicMock:
    group = MagicMock()
    group.level = level
    group.role_ids = role_ids
    return group


async def test_show_level_roles_no_permission(admin_command_info):
    admin_command_info.user.guild_permissions = make_permissions(manage_roles=False)
    await show_level_roles_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.show_level_roles.get_all_level_roles", new_callable=AsyncMock, return_value=[])
async def test_show_level_roles_empty(mock_roles, admin_command_info):
    await show_level_roles_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch(
    "commands.level.show_level_roles.get_all_level_roles",
    new_callable=AsyncMock,
    return_value=[_level_group(5, ["111", "222"])],
)
async def test_show_level_roles_with_data(mock_roles, admin_command_info):
    await show_level_roles_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def _capture_nested_classes(admin_command_info, level_roles):
    captured: dict = {}
    real_reply = admin_command_info.reply

    async def capture_reply(*args, **kwargs):
        frame = inspect.currentframe()
        while frame is not None:
            if frame.f_code.co_name == "show_level_roles_command":
                for name in (
                    "LevelRolesView",
                    "AddRoleView",
                    "AddRoleLevelModal",
                    "RemoveRoleView",
                    "RemoveRoleConfirmView",
                ):
                    if name in frame.f_locals:
                        captured[name] = frame.f_locals[name]
                break
            frame = frame.f_back
        return await real_reply(*args, **kwargs)

    admin_command_info.reply = AsyncMock(side_effect=capture_reply)
    with patch(
        "commands.level.show_level_roles.get_all_level_roles",
        new_callable=AsyncMock,
        return_value=level_roles,
    ):
        await show_level_roles_command(admin_command_info)
    return captured


@patch("commands.level.show_level_roles.add_level_role", new_callable=AsyncMock)
async def test_level_roles_nested_views(mock_add, admin_command_info):
    groups = [_level_group(i, [str(100 + i)]) for i in range(1, 4)]
    captured = await _capture_nested_classes(admin_command_info, groups)
    LevelRolesView = captured["LevelRolesView"]
    AddRoleView = captured["AddRoleView"]
    AddRoleLevelModal = captured["AddRoleLevelModal"]
    RemoveRoleView = captured["RemoveRoleView"]
    RemoveRoleConfirmView = captured["RemoveRoleConfirmView"]

    view = LevelRolesView(admin_command_info, groups)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.data = {"values": ["2|102"]}
    interaction.response.edit_message = AsyncMock()
    await view.on_select(interaction)

    view.current_page = 1
    view.update_options()
    next_interaction = make_view_interaction(admin_command_info.user)
    next_interaction.response.edit_message = AsyncMock()
    await view.next_page(next_interaction)

    view.current_page = 1
    view.update_options()
    prev_interaction = make_view_interaction(admin_command_info.user)
    prev_interaction.response.edit_message = AsyncMock()
    await view.previous_page(prev_interaction)

    add_interaction = make_view_interaction(admin_command_info.user)
    await view.add_role(add_interaction)
    add_interaction.response.send_message.assert_awaited_once()

    remove_interaction = make_view_interaction(admin_command_info.user)
    await view.remove_role(remove_interaction)
    remove_interaction.response.send_message.assert_awaited_once()

    add_view = AddRoleView(admin_command_info)
    role_interaction = make_view_interaction(admin_command_info.user)
    role_interaction.data = {"component_type": 3, "values": ["999"]}
    role_interaction.response.send_modal = AsyncMock()
    await add_view.interaction_check(role_interaction)

    cancel_interaction = make_view_interaction(admin_command_info.user)
    cancel_interaction.data = {"custom_id": "cancel_button", "component_type": 2}
    cancel_interaction.response.edit_message = AsyncMock()
    await add_view.interaction_check(cancel_interaction)

    modal = AddRoleLevelModal(admin_command_info, "999")
    modal.level.value = "5"
    submit = make_view_interaction(admin_command_info.user)
    submit.guild = admin_command_info.guild
    await modal.on_submit(submit)
    mock_add.assert_awaited_once()

    invalid_modal = AddRoleLevelModal(admin_command_info, "999")
    invalid_modal.level.value = "abc"
    bad = make_view_interaction(admin_command_info.user)
    await invalid_modal.on_submit(bad)
    bad.response.send_message.assert_awaited_once()

    remove_view = RemoveRoleView(admin_command_info, groups)
    sel = make_view_interaction(admin_command_info.user)
    sel.data = {"values": ["1|101"]}
    sel.response.send_message = AsyncMock()
    await remove_view.on_select(sel)

    remove_view.current_page = 0
    remove_view.update_options()
    rm_next = make_view_interaction(admin_command_info.user)
    rm_next.response.edit_message = AsyncMock()
    await remove_view.next_page(rm_next)

    confirm_view = RemoveRoleConfirmView(admin_command_info, ["1|101"])
    with patch("commands.level.show_level_roles.remove_level_role", new_callable=AsyncMock) as mock_rm:
        confirm = make_view_interaction(admin_command_info.user)
        confirm.guild = admin_command_info.guild
        confirm.response.edit_message = AsyncMock()
        await confirm_view.confirm(confirm, MagicMock())
        mock_rm.assert_awaited_once()

        cancel = make_view_interaction(admin_command_info.user)
        cancel.response.edit_message = AsyncMock()
        await confirm_view.cancel(cancel, MagicMock())

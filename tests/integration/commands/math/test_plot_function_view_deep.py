from __future__ import annotations

import ast

import numpy as np
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.math.plot_function import _safe_eval_node, plot_function_command
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs["view"]


def _interaction(user):
    interaction = make_view_interaction(user)
    interaction.message = MagicMock(edit=AsyncMock())
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.send_modal = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    return interaction


async def test_plotter_rename_with_functions(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.rename_function(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


async def test_plotter_update_plot(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    with patch.object(view.plotter, "generate_plot", AsyncMock(return_value=MagicMock())):
        await view.update_plot(interaction)
    interaction.response.defer.assert_awaited_once()
    interaction.edit_original_response.assert_awaited_once()


async def test_plotter_derivative_select(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    for child in view.children:
        if hasattr(child, "callback") and child.__class__.__name__ == "DerivativeSelect":
            interaction = _interaction(admin_command_info.user)
            child.values = ["0"]
            with patch.object(view, "update_plot", AsyncMock()):
                await child.callback(interaction)
            return
    pytest.skip("DerivativeSelect not found on view")


async def test_plotter_integrate_select_error(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    plotter = view.plotter
    with patch.object(plotter, "integrate_function", AsyncMock(side_effect=ValueError("bad"))):
        for child in view.children:
            if hasattr(child, "callback") and child.__class__.__name__ == "IntegrateSelect":
                interaction = _interaction(admin_command_info.user)
                child.values = ["0"]
                await child.callback(interaction)
                interaction.response.send_message.assert_awaited_once()
                return
    pytest.skip("IntegrateSelect not found on view")


async def test_plotter_rename_plot_modal(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.rename_plot(interaction, MagicMock())
    interaction.response.send_modal.assert_awaited_once()


async def test_plotter_change_axis_labels(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.change_x_label(interaction, MagicMock())
    await view.change_y_label(interaction, MagicMock())
    assert interaction.response.send_modal.await_count == 2


async def test_plotter_style_select_callback(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.change_style(interaction, MagicMock())
    edit_kwargs = interaction.response.edit_message.await_args.kwargs
    style_view = edit_kwargs.get("view")
    assert style_view is not None
    for child in style_view.children:
        if child.__class__.__name__ == "StyleSelect":
            sel = _interaction(admin_command_info.user)
            child.values = [child.options[0].value]
            with patch.object(view, "update_plot", AsyncMock()):
                await child.callback(sel)
            return
    pytest.skip("StyleSelect not found")


async def test_plot_constant_function(admin_command_info):
    await plot_function_command(admin_command_info, "42")
    admin_command_info.reply.assert_awaited_once()


def test_safe_eval_np_call():
    x = np.array([0.0, 1.0])
    node = ast.parse("np.sin(x)", mode="eval").body
    result = _safe_eval_node(node, x)
    np.testing.assert_array_almost_equal(result, np.sin(x))


def test_safe_eval_unsupported_attribute():
    node = ast.parse("np.unknown(x)", mode="eval").body
    with pytest.raises(ValueError):
        _safe_eval_node(node, 1.0)


def test_safe_eval_np_attr_not_allowed():
    node = ast.parse("np.fft", mode="eval").body
    with pytest.raises(TypeError):
        _safe_eval_node(node, 1.0)


def test_safe_eval_unsupported_call():
    node = ast.parse("abs(x)", mode="eval").body
    with pytest.raises(TypeError):
        _safe_eval_node(node, 1.0)


async def test_plotter_zoom_out_and_add_function(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    with patch.object(view, "update_plot", AsyncMock()):
        await view.zoom_out(interaction, MagicMock())
    interaction.response.defer.assert_not_called()
    add_i = _interaction(admin_command_info.user)
    add_i.response.send_modal = AsyncMock()
    await view.add_function(add_i, MagicMock())
    add_i.response.send_modal.assert_awaited_once()


async def test_plotter_interaction_check_wrong_user(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    assert await view.interaction_check(wrong) is False


async def test_plotter_add_function_modal_submit(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    interaction.response.send_modal = AsyncMock()
    await view.add_function(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args[0][0]
    modal.function_expression.value = "x+1"
    modal.function_name.value = "g"
    submit = _interaction(admin_command_info.user)
    with patch.object(view, "update_plot", AsyncMock()):
        await modal.on_submit(submit)
    assert len(view.plotter.functions) == 2


async def test_plotter_integrate_select_success(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    derive_i = _interaction(admin_command_info.user)
    await view.integrate(derive_i, MagicMock())
    integrate_view = derive_i.response.edit_message.await_args.kwargs["view"]
    for child in integrate_view.children:
        if child.__class__.__name__ == "IntegrateSelect":
            child.values = ["0"]
            sel_i = _interaction(admin_command_info.user)
            with patch.object(view, "update_plot", AsyncMock()):
                await child.callback(sel_i)
            return
    pytest.skip("IntegrateSelect not found")


async def test_plotter_derivative_select_success(admin_command_info):
    await plot_function_command(admin_command_info, "x**2")
    view = _view_from_reply(admin_command_info)
    derive_i = _interaction(admin_command_info.user)
    await view.derive(derive_i, MagicMock())
    derive_view = derive_i.response.edit_message.await_args.kwargs["view"]
    for child in derive_view.children:
        if child.__class__.__name__ == "DerivativeSelect":
            child.values = ["0"]
            sel_i = _interaction(admin_command_info.user)
            with patch.object(view, "update_plot", AsyncMock()):
                await child.callback(sel_i)
            return
    pytest.skip("DerivativeSelect not found")


async def test_plotter_rename_function_modal(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.rename_function(interaction, MagicMock())
    rename_view = interaction.response.edit_message.await_args.kwargs["view"]
    for child in rename_view.children:
        if child.__class__.__name__ == "RenameFunctionSelect":
            child.values = ["0"]
            sel_i = _interaction(admin_command_info.user)
            sel_i.response.send_modal = AsyncMock()
            await child.callback(sel_i)
            modal = sel_i.response.send_modal.await_args[0][0]
            modal.new_name.value = "line"
            submit = _interaction(admin_command_info.user)
            with patch.object(view, "update_plot", AsyncMock()):
                await modal.on_submit(submit)
            assert view.plotter.functions[0][2] == "line"
            return
    pytest.skip("RenameFunctionSelect not found")


async def test_plotter_change_title_modal(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    interaction.response.send_modal = AsyncMock()
    await view.rename_plot(interaction, MagicMock())
    modal = interaction.response.send_modal.await_args[0][0]
    modal.new_title.value = "My Plot"
    submit = _interaction(admin_command_info.user)
    with patch.object(view, "update_plot", AsyncMock()):
        await modal.on_submit(submit)
    assert view.plotter.plot_title == "My Plot"

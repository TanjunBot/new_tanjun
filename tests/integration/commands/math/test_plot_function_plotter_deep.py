from __future__ import annotations

import ast

import numpy as np
import pytest
from unittest.mock import AsyncMock, MagicMock

from commands.math.plot_function import _safe_eval_node, plot_function_command
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


async def test_plotter_intersection_single_function(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    plotter = _view_from_reply(admin_command_info).plotter
    assert await plotter.find_intersection_points() == []


async def test_plotter_find_extrema_parabola(admin_command_info):
    await plot_function_command(admin_command_info, "sin(x)", x_min=-3, x_max=3)
    plotter = _view_from_reply(admin_command_info).plotter
    extrema = await plotter.find_extrema(plotter.functions[0][1])
    assert len(extrema) >= 1


async def test_plotter_find_inflection_cubic(admin_command_info):
    await plot_function_command(admin_command_info, "x**3", x_min=-2, x_max=2)
    plotter = _view_from_reply(admin_command_info).plotter
    points = await plotter.find_inflection_points(plotter.functions[0][1])
    assert isinstance(points, list)


async def test_plotter_find_zeros_extrema_inflection(admin_command_info):
    await plot_function_command(admin_command_info, "x**2 - 4", x_min=-5, x_max=5)
    plotter = _view_from_reply(admin_command_info).plotter
    func = plotter.functions[0][1]
    zeros = await plotter.find_zeros(func)
    assert isinstance(zeros, list)
    extrema = await plotter.find_extrema(func)
    assert isinstance(extrema, list)
    points = await plotter.find_inflection_points(func)
    assert isinstance(points, list)


async def test_plotter_intersection_two_functions(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    plotter = _view_from_reply(admin_command_info).plotter
    await plotter.add_function("2*x", "g")
    intersections = await plotter.find_intersection_points()
    assert isinstance(intersections, list)


async def test_plotter_rename_and_integrate(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    plotter = _view_from_reply(admin_command_info).plotter
    await plotter.rename_function(0, "line")
    assert plotter.functions[0][2] == "line"
    await plotter.integrate_function("x", "line")
    assert len(plotter.functions) == 2


async def test_plotter_view_zoom_and_move(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.zoom_in(interaction, MagicMock())
    await view.move_up(interaction, MagicMock())
    await view.move_down(interaction, MagicMock())
    await view.move_left(interaction, MagicMock())
    await view.move_right(interaction, MagicMock())
    interaction.response.send_message.assert_not_called()


async def test_plotter_view_derive_integrate_buttons(admin_command_info):
    await plot_function_command(admin_command_info, "x**2")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.derive(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()
    await view.integrate(interaction, MagicMock())
    assert interaction.response.edit_message.await_count == 2


async def test_plotter_view_rename_no_functions(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    view.plotter.functions.clear()
    interaction = _interaction(admin_command_info.user)
    await view.rename_function(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_plotter_view_change_style(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.change_style(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


async def test_plotter_view_empty_button(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    interaction = _interaction(admin_command_info.user)
    await view.empty(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


def test_safe_eval_all_operators():
    x = np.array([1.0, 2.0])
    node = ast.parse("x - 1", mode="eval").body
    np.testing.assert_array_almost_equal(_safe_eval_node(node, x), [0.0, 1.0])
    node = ast.parse("x * 2", mode="eval").body
    np.testing.assert_array_almost_equal(_safe_eval_node(node, x), [2.0, 4.0])
    node = ast.parse("x / 2", mode="eval").body
    np.testing.assert_array_almost_equal(_safe_eval_node(node, x), [0.5, 1.0])
    node = ast.parse("x % 2", mode="eval").body
    np.testing.assert_array_almost_equal(_safe_eval_node(node, x), [1.0, 0.0])
    node = ast.parse("x ** 2", mode="eval").body
    np.testing.assert_array_almost_equal(_safe_eval_node(node, x), [1.0, 4.0])
    node = ast.parse("-x", mode="eval").body
    np.testing.assert_array_almost_equal(_safe_eval_node(node, x), [-1.0, -2.0])
    node = ast.parse("+x", mode="eval").body
    np.testing.assert_array_almost_equal(_safe_eval_node(node, x), [1.0, 2.0])


@pytest.mark.asyncio
async def test_plotter_view_on_timeout(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    view = _view_from_reply(admin_command_info)
    view.message = MagicMock(edit=AsyncMock())
    await view.on_timeout()
    view.message.edit.assert_awaited_once()

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from commands.math.calculator import CalculatorButton, CalculatorView
from tests.helpers.discord import make_interaction

pytestmark = pytest.mark.asyncio


def _calc_interaction(user):
    interaction = make_interaction(user=user)
    interaction.response.edit_message = AsyncMock()
    return interaction


async def test_calculator_page2_log10(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 2
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "log10")
    assert view.equation == "log10("
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_page2_floor_ceil(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 2
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "left_floor")
    assert view.equation == "floor("
    await view.button_callback(interaction, "right_floor")
    assert view.equation.endswith(")")
    interaction.response.edit_message.assert_awaited()


async def test_calculator_page2_divide_add(admin_command_info):
    view = CalculatorView(admin_command_info, "4")
    view.equation = "4"
    view.display_equation = "4"
    view.current_page = 2
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "divide")
    assert view.equation == "4/"
    await view.button_callback(interaction, "add")
    assert view.equation == "4/+"
    interaction.response.edit_message.assert_awaited()


async def test_calculator_button_callback(admin_command_info):
    view = CalculatorView(admin_command_info)
    btn = CalculatorButton("7", style=1, custom_id="7", row=0)
    btn.view = view
    interaction = _calc_interaction(admin_command_info.user)
    await btn.callback(interaction)
    assert view.equation == "7"
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_tan_cos_page1(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 1
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "tan")
    assert view.equation == "tan("
    await view.button_callback(interaction, "cos")
    assert "cos(" in view.equation
    interaction.response.edit_message.assert_awaited()


async def test_calculator_modulo_and_e(admin_command_info):
    view = CalculatorView(admin_command_info)
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "modulo")
    assert view.equation == "%"
    await view.button_callback(interaction, "e")
    assert view.equation == "%e"
    interaction.response.edit_message.assert_awaited()


async def test_calculator_backspace_log10(admin_command_info):
    view = CalculatorView(admin_command_info, "log10(")
    view.equation = "log10("
    view.display_equation = "log10("
    view.current_page = 2
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_page2_ln_sqrt(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 2
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "ln")
    assert view.equation == "ln("
    await view.button_callback(interaction, "sqrt")
    assert "sqrt(" in view.equation
    interaction.response.edit_message.assert_awaited()


async def test_calculator_button_no_view(admin_command_info):
    btn = CalculatorButton("7", style=1, custom_id="7", row=0)
    btn.view = None
    interaction = _calc_interaction(admin_command_info.user)
    await btn.callback(interaction)
    interaction.response.edit_message.assert_not_called()


async def test_calculator_clear_after_result(admin_command_info):
    view = CalculatorView(admin_command_info, "2+2")
    view.equation = "2+2"
    view.display_equation = "2+2"
    view.result = "4.0"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "7")
    assert view.equation == "7"
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_interaction_check_ok(admin_command_info):
    view = CalculatorView(admin_command_info)
    interaction = _calc_interaction(admin_command_info.user)
    assert await view.interaction_check(interaction) is True


async def test_calculator_backspace_asin(admin_command_info):
    view = CalculatorView(admin_command_info, "asin(")
    view.equation = "asin("
    view.display_equation = "asin("
    view.current_page = 1
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_backspace_log2_ln(admin_command_info):
    view = CalculatorView(admin_command_info, "log2(")
    view.equation = "log2("
    view.display_equation = "log2("
    view.current_page = 2
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    view.equation = "ln("
    view.display_equation = "ln("
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    interaction.response.edit_message.assert_awaited()


async def test_calculator_backspace_floor_ceil_abs(admin_command_info):
    view = CalculatorView(admin_command_info, "floor(")
    view.equation = "floor("
    view.display_equation = "floor("
    view.current_page = 2
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    view.equation = "ceil("
    view.display_equation = "ceil("
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    view.equation = "abs("
    view.display_equation = "abs("
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    interaction.response.edit_message.assert_awaited()


async def test_calculator_variables_and_nthroot(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 1
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "x")
    await view.button_callback(interaction, "nthroot")
    assert "nthroot(" in view.equation
    await view.button_callback(interaction, "square")
    assert "^(2)" in view.equation
    interaction.response.edit_message.assert_awaited()


async def test_calculator_page2_ceil_buttons(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 2
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "left_ceil")
    assert view.equation == "ceil("
    await view.button_callback(interaction, "right_ceil")
    assert view.equation.endswith(")")
    interaction.response.edit_message.assert_awaited()


async def test_calculator_assign_eval_error(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 1
    view.equation = "x:=bad++"
    view.display_equation = "x:=bad++"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "assign")
    assert view.equation == ""
    interaction.response.edit_message.assert_awaited_once()

import pytest
from unittest.mock import AsyncMock, MagicMock

import discord

from commands.math.calculator import CalculatorView, calculator_command
from tests.helpers.discord import make_command_info, make_interaction, make_member

pytestmark = pytest.mark.asyncio


def _calc_interaction(user):
    interaction = make_interaction(user=user)
    interaction.response.edit_message = AsyncMock()
    return interaction


async def test_calculator_command_success(admin_command_info):
    await calculator_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs
    assert "view" in call_kwargs


async def test_calculator_command_with_initial_equation(admin_command_info):
    await calculator_command(admin_command_info, "2+2")
    admin_command_info.reply.assert_awaited_once()


async def test_calculator_clear_button(admin_command_info):
    view = CalculatorView(admin_command_info, "123")
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "clear")
    assert view.equation == ""
    assert view.display_equation == ""
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_equals_success(admin_command_info):
    view = CalculatorView(admin_command_info, "2+2")
    view.equation = "2+2"
    view.display_equation = "2+2"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "equals")
    assert view.result == "4.0"
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_equals_invalid(admin_command_info):
    view = CalculatorView(admin_command_info, "2++")
    view.equation = "2++"
    view.display_equation = "2++"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "equals")
    assert "Error" in view.result
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_backspace(admin_command_info):
    view = CalculatorView(admin_command_info, "123")
    view.equation = "123"
    view.display_equation = "123"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "backspace")
    assert view.equation == "12"
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_backspace_sin(admin_command_info):
    view = CalculatorView(admin_command_info, "sin(")
    view.equation = "sin("
    view.display_equation = "sin("
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "backspace")
    assert view.equation == ""
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_next_page(admin_command_info):
    view = CalculatorView(admin_command_info)
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "next_page")
    assert view.current_page == 1
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_prev_page(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 1
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "prev_page")
    assert view.current_page == 0
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_add_digit(admin_command_info):
    view = CalculatorView(admin_command_info)
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "5")
    assert view.equation == "5"
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_multiply_operator(admin_command_info):
    view = CalculatorView(admin_command_info, "2")
    view.equation = "2"
    view.display_equation = "2"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "multiply")
    assert view.equation == "2*"
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_pi_button(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 0
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "pi")
    assert view.equation == "pi"
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_sin_function(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 1
    view.create_buttons()
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "sin")
    assert view.equation == "sin("
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_unauthorized_user(admin_command_info):
    view = CalculatorView(admin_command_info)
    other_user = make_member(user_id=999999999)
    interaction = make_interaction(user=other_user)
    result = await view.interaction_check(interaction)
    assert result is False
    interaction.response.send_message.assert_awaited_once()


async def test_calculator_assign_success(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 1
    view.equation = "x:=2+2"
    view.display_equation = "x:=2+2"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "assign")
    assert view.variables.get("x") == 4
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_assign_invalid(admin_command_info):
    view = CalculatorView(admin_command_info)
    view.current_page = 1
    view.equation = "invalid"
    view.display_equation = "invalid"
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "assign")
    assert view.equation == ""
    interaction.response.edit_message.assert_awaited_once()


async def test_calculator_on_timeout(admin_command_info):
    view = CalculatorView(admin_command_info)
    message = MagicMock()
    message.edit = AsyncMock()
    view.set_message(message)
    await view.on_timeout()
    message.edit.assert_awaited_once()


async def test_calculator_decimal_button(admin_command_info):
    view = CalculatorView(admin_command_info)
    interaction = _calc_interaction(admin_command_info.user)
    await view.button_callback(interaction, "decimal")
    assert view.equation == "0."
    interaction.response.edit_message.assert_awaited_once()

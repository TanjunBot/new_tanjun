import numpy as np
import pytest
from unittest.mock import AsyncMock, MagicMock

from commands.math.plot_function import (
    _safe_eval_node,
    _safe_np_eval,
    plot_function_command,
)


pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_plot_function_command_success(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    admin_command_info.reply.assert_awaited_once()
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert "embed" in call_kwargs
    assert "view" in call_kwargs


async def test_plot_function_command_with_bounds(admin_command_info):
    await plot_function_command(admin_command_info, "x**2", x_min=-5, x_max=5)
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_constant(admin_command_info):
    await plot_function_command(admin_command_info, "42")
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_trig(admin_command_info):
    await plot_function_command(admin_command_info, "sin(x)")
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_linear(admin_command_info):
    await plot_function_command(admin_command_info, "2*x+1")
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_exp(admin_command_info):
    await plot_function_command(admin_command_info, "exp(x)")
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_log(admin_command_info):
    await plot_function_command(admin_command_info, "log(x)", x_min=0.1, x_max=10)
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_sqrt(admin_command_info):
    await plot_function_command(admin_command_info, "sqrt(x)", x_min=0, x_max=10)
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_caret_syntax(admin_command_info):
    await plot_function_command(admin_command_info, "x^2")
    admin_command_info.reply.assert_awaited_once()


async def test_plot_function_command_implicit_multiply(admin_command_info):
    await plot_function_command(admin_command_info, "2x")
    admin_command_info.reply.assert_awaited_once()


def test_safe_np_eval_polynomial():
    x = np.array([0.0, 1.0, 2.0])
    result = _safe_np_eval("x**2 + 2*x + 1", x)
    np.testing.assert_array_almost_equal(result, [1.0, 4.0, 9.0])


def test_safe_np_eval_np_sin():
    x = np.array([0.0, np.pi / 2])
    result = _safe_np_eval("np.sin(x)", x)
    np.testing.assert_array_almost_equal(result, [0.0, 1.0])


def test_safe_np_eval_scalar():
    result = _safe_np_eval("3 + 4", 0)
    assert result == 7


def test_safe_eval_node_unknown_variable():
    import ast

    node = ast.parse("y + 1", mode="eval").body
    with pytest.raises(ValueError, match="Unknown variable"):
        _safe_eval_node(node, 0)


def test_safe_eval_node_non_numeric_constant():
    import ast

    node = ast.parse("'hello'", mode="eval").body
    with pytest.raises(ValueError, match="Non-numeric constant"):
        _safe_eval_node(node, 0)


def test_safe_eval_node_unsupported_operator():
    import ast

    node = ast.parse("x << 1", mode="eval").body
    with pytest.raises(TypeError):
        _safe_eval_node(node, 1)


def test_safe_eval_node_unsupported_unary():
    import ast

    node = ast.parse("~x", mode="eval").body
    with pytest.raises(TypeError):
        _safe_eval_node(node, 1)


def test_safe_eval_node_disallowed_np_function():
    with pytest.raises(ValueError):
        _safe_np_eval("np.fft(x)", 1)


async def test_plot_function_reply_includes_file(admin_command_info):
    await plot_function_command(admin_command_info, "x")
    call_kwargs = admin_command_info.reply.await_args.kwargs
    assert call_kwargs.get("file") is not None

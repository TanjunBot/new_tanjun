from __future__ import annotations

from diagnostics.specs._helpers import register_kwargs, register_method_commands

_MATH_COMMANDS = {
    "calc": "calcCommand",
    "calculator": "calculator_command",
    "num2word": "num2word_command",
    "random_number": "random_number_command",
    "plot_function": "plot_function_command",
    "faculty": "faculty_command",
}


def register() -> None:
    for method in _MATH_COMMANDS:
        register_kwargs(f"math.MathCommands.{method}", {})
    register_method_commands("math", "MathCommands", _MATH_COMMANDS)

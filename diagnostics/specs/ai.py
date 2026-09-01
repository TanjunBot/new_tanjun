from __future__ import annotations

from diagnostics.specs._helpers import register_kwargs, register_method_commands


def register() -> None:
    register_method_commands(
        "ai",
        "CustomSituationCommands",
        {"add_custom": "add_custom_situation", "delete_custom": "delete_custom_situation"},
    )
    register_method_commands(
        "ai",
        "AiCommands",
        {
            "ask_custom_situation": "ask_gpt",
            "ask_gpt_command": "ask_gpt",
            "ask_tanjuwun_command": "ask_gpt",
        },
    )
    register_kwargs(
        "ai.CustomSituationCommands.add_custom",
        lambda: {
            "name": "test",
            "personality": "You are a helpful assistant for diagnostics.",
            "temperature": 1.0,
            "topp": 1.0,
            "frequencypenalty": 0.0,
            "presencepenalty": 0.0,
        },
    )
    register_kwargs(
        "ai.AiCommands.ask_custom_situation",
        lambda: {"prompt": "hello", "personality": "default"},
    )
    register_kwargs(
        "ai.AiCommands.ask_gpt_command",
        lambda: {
            "prompt": "hello",
            "temperature": 1.0,
            "topp": 1.0,
            "frequencypenalty": 0.0,
            "presencepenalty": 0.0,
        },
    )
    register_kwargs(
        "ai.AiCommands.ask_tanjuwun_command",
        lambda: {
            "prompt": "hello",
            "temperature": 1.0,
            "topp": 1.0,
            "frequencypenalty": 0.0,
            "presencepenalty": 0.0,
        },
    )

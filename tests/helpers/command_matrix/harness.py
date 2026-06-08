from __future__ import annotations

import importlib
from contextlib import contextmanager
from typing import Any, Iterator
from unittest.mock import AsyncMock, patch

from diagnostics.kwargs_defaults import build_kwargs_for_handler
from tests.helpers.command_matrix.dimensions import (
    kwargs_for_matrix_case,
    option_overrides_for_matrix_case,
)
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.permission_profiles import PermissionProfile, command_info_for_permission
from tests.helpers.live_e2e.models import CommandLiveCase


def build_e2e_live_case(case: MatrixCase) -> CommandLiveCase:
    overrides = option_overrides_for_matrix_case(case)
    profile = _assert_profile_for_group(case.group)
    return CommandLiveCase(
        tree_path=case.tree_path,
        option_overrides=overrides,
        assert_profile=profile,
        response_kind="embed",
    )


def _assert_profile_for_group(group: str) -> str:
    if group == "funcmd_name":
        return "fun"
    if group == "math_name":
        return "math"
    if group.startswith("admin_"):
        return "admin"
    if group == "games_name":
        return "games"
    if group == "setup_name":
        return "setup"
    if group == "ai_name":
        return "ai"
    if group.startswith("utility"):
        return "utility"
    if group.startswith("level"):
        return "level"
    if group == "giveaway_name":
        return "giveaway"
    if group == "image_name":
        return "image"
    if group in {"channel_name", "logs_name", "minigame_name"}:
        return group.removesuffix("_name")
    return "default"


def permission_for_case(case: MatrixCase) -> PermissionProfile:
    profile = case.dimension("permission", "admin")
    if profile in {
        "admin",
        "member",
        "restricted",
        "no_guild",
        "channel_deny_send",
        "channel_deny_embed",
    }:
        return profile  # type: ignore[return-value]
    return "admin"


def find_spec_for_path(tree_path: str):
    from diagnostics.registry import all_specs

    for spec in all_specs():
        if spec.tree_path == tree_path:
            return spec
    return None


def resolve_handler_module(tree_path: str) -> tuple[str, str] | None:
    spec = find_spec_for_path(tree_path)
    if spec is None:
        return None
    group_cls = spec.group_cls
    method = spec.method_name
    module = group_cls.__module__
    if module.startswith("commands."):
        return module, method
    return None


@contextmanager
def matrix_patches(case: MatrixCase) -> Iterator[None]:
    from tests.helpers.command_matrix.patches import matrix_patches as _patches

    with _patches(case):
        yield


async def invoke_command_for_case(case: MatrixCase, info: Any) -> None:
    import inspect

    from diagnostics.kwargs_defaults import build_kwargs_for_handler
    from tests.helpers.command_matrix.resolver import resolve_command_callable

    handler = resolve_command_callable(case.tree_path)
    if handler is None:
        raise RuntimeError(f"No command handler resolved for {case.tree_path!r}")
    extra = kwargs_for_matrix_case(case)
    kwargs = build_kwargs_for_handler(handler)
    kwargs.update(extra)
    kwargs.pop("command_info", None)
    kwargs.pop("info", None)
    try:
        sig = inspect.signature(handler)
    except (TypeError, ValueError):
        await handler(info, **kwargs)
        return
    param_names = set(sig.parameters)
    allowed = {k: v for k, v in kwargs.items() if k in param_names}
    if "ctx" in param_names and "ctx" not in allowed:
        from diagnostics.mocks import make_interaction

        interaction = make_interaction(
            user=info.user,
            guild=getattr(info, "guild", None),
            channel=getattr(info, "channel", None),
            locale=str(getattr(info, "locale", "en-US")),
        )
        info._matrix_interaction = interaction
        allowed["ctx"] = interaction
    if param_names & {"command_info", "info"}:
        await handler(info, **allowed)
    else:
        await handler(**allowed)


async def invoke_handler_for_case(case: MatrixCase, info: Any) -> None:
    extra = kwargs_for_matrix_case(case)
    if case.group == "math_name":
        command = case.dimension("command")
        from tests.helpers.command_matrix.dimensions import EXPRESSION_VALUES

        expression = EXPRESSION_VALUES.get(case.dimension("expression"), "2+2")
        if command == "calc":
            from commands.math.calc import calc

            await calc(info, expression)
            return
        if command == "calculator":
            from commands.math.calculator import calculator_command

            await calculator_command(info, expression)
            return
        if command == "faculty":
            from commands.math.faculty import faculty_command

            await faculty_command(info, 5)
            return
        if command == "num2word":
            from commands.math.num2word import num2word

            await num2word(info, 42, "en")
            return
        if command == "plotfunction":
            from commands.math.plot_function import plot_function_command

            await plot_function_command(info, "x")
            return
        if command == "randomnumber":
            from commands.math.randomnumber import random_number_command

            await random_number_command(info, 1, 10)
            return
    if case.group == "funcmd_name":
        from commands.fun.funcommands import fun_command

        action = case.dimension("action")
        from tests.helpers.fun_matrix import MESSAGE_VARIANTS

        message_kind = case.dimension("message_kind", "none")
        message = MESSAGE_VARIANTS.get(message_kind)
        from tests.helpers.discord import make_member

        target = extra.get("user") or make_member(user_id=222222222222222222, name="Target")
        await fun_command(info, action, target, message)
        return
    await invoke_command_for_case(case, info)

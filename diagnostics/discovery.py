from __future__ import annotations

import importlib
import inspect
from typing import Any, Optional

from discord import app_commands

from diagnostics.assertions import expect_interaction_response
from diagnostics.kwargs_defaults import build_kwargs_for_handler
from diagnostics.models import CommandBehaviorSpec
from diagnostics.specs.overrides import (
    SPEC_CUSTOM_ASSERTIONS,
    SPEC_OVERRIDES,
    SPEC_PATCH_TARGETS,
    SPEC_SKIPS,
)

SLASH_EXTENSIONS = (
    "extensions.admin",
    "extensions.ai",
    "extensions.channel",
    "extensions.fun",
    "extensions.games",
    "extensions.giveaway",
    "extensions.image",
    "extensions.level",
    "extensions.logs",
    "extensions.math",
    "extensions.minigames",
    "extensions.setup_wizards",
    "extensions.utility",
)


def _instantiate_group(group_cls: type) -> Optional[Any]:
    from unittest.mock import MagicMock

    try:
        return group_cls(name="diag", description="diag")
    except TypeError:
        pass
    try:
        return group_cls()
    except TypeError:
        pass
    try:
        return group_cls(MagicMock())
    except TypeError:
        return None


def _find_group_classes(module: Any) -> list[type]:
    classes: list[type] = []
    group_base = app_commands.Group
    if not isinstance(group_base, type):
        return classes
    for _name, obj in inspect.getmembers(module, inspect.isclass):
        try:
            if not issubclass(obj, group_base):
                continue
        except TypeError:
            continue
        if obj is app_commands.Group:
            continue
        if obj.__module__ != module.__name__:
            continue
        classes.append(obj)
    return classes


def _resolve_extra_kwargs(spec_id: str, handler: Any) -> dict[str, Any] | Any:
    override = SPEC_OVERRIDES.get(spec_id)
    if override is not None:
        if callable(override) and not isinstance(override, dict):
            result = override()
            return dict(result) if isinstance(result, dict) else {}
        if isinstance(override, dict):
            return dict(override)
    return build_kwargs_for_handler(handler)


def discover_extension_specs(extension: str) -> list[CommandBehaviorSpec]:
    module = importlib.import_module(extension)
    specs: list[CommandBehaviorSpec] = []
    ext_short = extension.rsplit(".", 1)[-1]

    for group_cls in _find_group_classes(module):
        group = _instantiate_group(group_cls)
        if group is None:
            continue
        command_entries: list[tuple[str, Any]] = []
        if hasattr(group, "walk_commands"):
            for command in group.walk_commands():
                callback = command.callback
                command_entries.append((callback.__name__, callback))
        else:
            for method_name, method in inspect.getmembers(group, predicate=inspect.iscoroutinefunction):
                if method_name.startswith("_") or method_name in ("interaction_check", "on_error"):
                    continue
                try:
                    sig = inspect.signature(method)
                except (TypeError, ValueError):
                    continue
                if "interaction" in sig.parameters or "ctx" in sig.parameters:
                    command_entries.append((method_name, method))

        for method_name, callback in command_entries:
            if method_name in ("interaction_check", "on_error"):
                continue

            spec_id = f"{ext_short}.{group_cls.__name__}.{method_name}"
            skip_reason = SPEC_SKIPS.get(spec_id)
            handler = callback
            specs.append(
                CommandBehaviorSpec(
                    id=spec_id,
                    extension=extension,
                    group_cls=group_cls,
                    method_name=method_name,
                    extra_kwargs=_resolve_extra_kwargs(spec_id, handler),
                    skip_reason=skip_reason,
                    assertions=SPEC_CUSTOM_ASSERTIONS.get(spec_id, expect_interaction_response),
                    patch_targets=SPEC_PATCH_TARGETS.get(spec_id, ()),
                )
            )
    return specs


def discover_all_specs() -> list[CommandBehaviorSpec]:
    specs: list[CommandBehaviorSpec] = []
    for extension in SLASH_EXTENSIONS:
        specs.extend(discover_extension_specs(extension))
    return specs

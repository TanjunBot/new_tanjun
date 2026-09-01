from __future__ import annotations

import importlib
import inspect
from collections.abc import Iterator
from typing import Any, Optional

from discord import app_commands
from discord.ext import commands

from diagnostics.assertions import expect_interaction_response
from diagnostics.kwargs_defaults import build_kwargs_for_handler
from diagnostics.models import CommandBehaviorSpec
from diagnostics.tree import load_manifest
from diagnostics.specs.overrides import (
    SPEC_CUSTOM_ASSERTIONS,
    SPEC_OVERRIDES,
    SPEC_PATCH_EXCLUDE,
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


def _find_cog_classes(module: Any) -> list[type]:
    classes: list[type] = []
    seen: set[type] = set()
    for _name, obj in inspect.getmembers(module, inspect.isclass):
        try:
            if not issubclass(obj, commands.Cog):
                continue
        except TypeError:
            continue
        if obj is commands.Cog:
            continue
        if obj.__module__ != module.__name__:
            continue
        if obj in seen:
            continue
        seen.add(obj)
        classes.append(obj)
    return classes


def _find_group_classes(module: Any) -> list[type]:
    classes: list[type] = []
    seen: set[type] = set()
    group_base: type = app_commands.Group
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
        if obj in seen:
            continue
        seen.add(obj)
        classes.append(obj)
    return classes


def _locale_name(value: Any) -> str:
    if value is None:
        return ""
    key = getattr(value, "key", None)
    if key is not None:
        return str(key)
    message = getattr(value, "message", None)
    if isinstance(message, str):
        return message
    return str(value)


def _command_leaf_name(command: Any, method_name: str) -> str:
    name = getattr(command, "name", None)
    if name is not None:
        return _locale_name(name)
    return method_name


def _manifest_paths_by_leaf() -> dict[str, list[str]]:
    paths = load_manifest().get("paths") or []
    by_leaf: dict[str, list[str]] = {}
    for path in paths:
        leaf = path.rsplit(" ", 1)[-1]
        by_leaf.setdefault(leaf, []).append(path)
    return by_leaf


def _resolve_manifest_tree_path(leaf: str, provisional: str, by_leaf: dict[str, list[str]]) -> str:
    candidates = by_leaf.get(leaf, [])
    if not candidates:
        return provisional
    if len(candidates) == 1:
        return candidates[0]
    prov_parts = [p for p in (_locale_name(part) for part in provisional.split()) if p and p != "diag"]
    if prov_parts:
        narrowed = [path for path in candidates if all(part in path.split() for part in prov_parts)]
        if len(narrowed) == 1:
            return narrowed[0]
    return provisional


def _resolve_extra_kwargs(spec_id: str, handler: Any) -> dict[str, Any] | Any:
    override = SPEC_OVERRIDES.get(spec_id)
    if override is not None:
        if callable(override) and not isinstance(override, dict):
            result = override()
            return dict(result) if isinstance(result, dict) else {}
        if isinstance(override, dict):
            return dict(override)
    return build_kwargs_for_handler(handler)


def _iter_command_leaves(commands_list: list[Any], prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:
    for cmd in commands_list:
        name = getattr(cmd, "name", None)
        if not name:
            continue
        path = (*prefix, _locale_name(name))
        children = list(getattr(cmd, "commands", []) or [])
        if children:
            yield from _iter_command_leaves(children, path)
        else:
            yield path, cmd


def _tree_path_for_command(command: Any, method_name: str) -> str:
    parts: list[str] = []
    parent = getattr(command, "parent", None)
    while parent is not None and getattr(parent, "name", None):
        parts.append(_locale_name(parent.name))
        parent = getattr(parent, "parent", None)
    parts.reverse()
    name = getattr(command, "name", None) or method_name
    parts.append(_locale_name(name))
    return " ".join(parts)


def _discover_cog_specs(
    extension: str,
    ext_short: str,
    paths_by_leaf: dict[str, list[str]],
) -> list[CommandBehaviorSpec]:
    module = importlib.import_module(extension)
    specs: list[CommandBehaviorSpec] = []
    for cog_cls in _find_cog_classes(module):
        seen_ids: set[str] = set()
        for command in getattr(cog_cls, "__cog_app_commands__", ()) or ():
            callback = command.callback
            method_name = getattr(callback, "__name__", "unknown")
            if method_name in ("interaction_check", "on_error"):
                continue
            spec_id = f"{ext_short}.{cog_cls.__name__}.{method_name}"
            if spec_id in seen_ids:
                continue
            seen_ids.add(spec_id)
            leaf = _locale_name(command.name)
            manifest_path = _resolve_manifest_tree_path(leaf, leaf, paths_by_leaf)
            skip_reason = SPEC_SKIPS.get(spec_id)
            specs.append(
                CommandBehaviorSpec(
                    id=spec_id,
                    extension=extension,
                    group_cls=cog_cls,
                    method_name=method_name,
                    tree_path=manifest_path,
                    extra_kwargs=_resolve_extra_kwargs(spec_id, callback),
                    skip_reason=skip_reason,
                    assertions=SPEC_CUSTOM_ASSERTIONS.get(spec_id, expect_interaction_response),
                    patch_targets=SPEC_PATCH_TARGETS.get(spec_id, ()),
                    patch_exclude=SPEC_PATCH_EXCLUDE.get(spec_id, ()),
                )
            )
    return specs


def discover_extension_specs(extension: str) -> list[CommandBehaviorSpec]:
    module = importlib.import_module(extension)
    specs: list[CommandBehaviorSpec] = []
    ext_short = extension.rsplit(".", 1)[-1]

    paths_by_leaf = _manifest_paths_by_leaf()

    specs.extend(_discover_cog_specs(extension, ext_short, paths_by_leaf))

    for group_cls in _find_group_classes(module):
        group = _instantiate_group(group_cls)
        if group is None:
            continue
        root_commands = list(getattr(group, "commands", []) or [])
        command_entries: list[tuple[str, str, Any]] = []
        if root_commands:
            for path_parts, command in _iter_command_leaves(root_commands):
                callback = command.callback
                command_entries.append((" ".join(path_parts), getattr(callback, '__name__', 'unknown'), command))
        elif hasattr(group, "walk_commands"):
            for command in group.walk_commands():
                callback = command.callback
                method_name = getattr(callback, '__name__', 'unknown')
                command_entries.append(
                    (_tree_path_for_command(command, method_name), method_name, command)
                )
        else:
            for method_name, method in inspect.getmembers(group, predicate=inspect.iscoroutinefunction):
                if method_name.startswith("_") or method_name in ("interaction_check", "on_error"):
                    continue
                try:
                    sig = inspect.signature(method)
                except (TypeError, ValueError):
                    continue
                if "interaction" in sig.parameters or "ctx" in sig.parameters:
                    command_entries.append((method_name, method_name, method))

        seen_ids: set[str] = set()
        for tree_path, method_name, command in command_entries:
            if method_name in ("interaction_check", "on_error"):
                continue

            spec_id = f"{ext_short}.{group_cls.__name__}.{method_name}"
            if spec_id in seen_ids:
                continue
            seen_ids.add(spec_id)
            skip_reason = SPEC_SKIPS.get(spec_id)
            handler = command.callback if hasattr(command, "callback") else command
            leaf = _command_leaf_name(command, method_name)
            manifest_path = _resolve_manifest_tree_path(leaf, tree_path, paths_by_leaf)
            specs.append(
                CommandBehaviorSpec(
                    id=spec_id,
                    extension=extension,
                    group_cls=group_cls,
                    method_name=method_name,
                    tree_path=manifest_path,
                    extra_kwargs=_resolve_extra_kwargs(spec_id, handler),
                    skip_reason=skip_reason,
                    assertions=SPEC_CUSTOM_ASSERTIONS.get(spec_id, expect_interaction_response),
                    patch_targets=SPEC_PATCH_TARGETS.get(spec_id, ()),
                    patch_exclude=SPEC_PATCH_EXCLUDE.get(spec_id, ()),
                )
            )
    return specs


def discover_all_specs() -> list[CommandBehaviorSpec]:
    specs: list[CommandBehaviorSpec] = []
    for extension in SLASH_EXTENSIONS:
        specs.extend(discover_extension_specs(extension))
    return specs

from __future__ import annotations

import ast
import importlib
import inspect
import textwrap
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
_HANDLERS_JSON = ROOT / "coverage" / "command_handlers.json"
_HANDLER_CACHE: dict[str, Callable[..., Any] | None] = {}
_STATIC_BY_PATH: dict[str, str] | None = None
_STATIC_BY_SPEC: dict[str, str] | None = None


def find_spec_for_path(tree_path: str):
    try:
        from diagnostics.registry import all_specs

        for spec in all_specs():
            if spec.tree_path == tree_path:
                return spec
    except Exception:
        return None
    return None


def _load_static_handlers() -> tuple[dict[str, str], dict[str, str]]:
    global _STATIC_BY_PATH, _STATIC_BY_SPEC
    if _STATIC_BY_PATH is not None and _STATIC_BY_SPEC is not None:
        return _STATIC_BY_PATH, _STATIC_BY_SPEC
    if not _HANDLERS_JSON.is_file():
        _STATIC_BY_PATH, _STATIC_BY_SPEC = {}, {}
        return _STATIC_BY_PATH, _STATIC_BY_SPEC
    import json

    data = json.loads(_HANDLERS_JSON.read_text(encoding="utf-8"))
    _STATIC_BY_PATH = dict(data.get("by_path") or {})
    _STATIC_BY_SPEC = dict(data.get("by_spec") or {})
    return _STATIC_BY_PATH, _STATIC_BY_SPEC


def _load_callable(handler_path: str) -> Callable[..., Any] | None:
    if "." not in handler_path:
        return None
    module_path, func_name = handler_path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        return None
    fn = getattr(module, func_name, None)
    return fn if callable(fn) else None


def _import_alias_map(module_path: str) -> dict[str, str]:
    path = ROOT / (module_path.replace(".", "/") + ".py")
    if not path.is_file():
        return {}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return {}
    mapping: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or not node.module or not node.module.startswith("commands."):
            continue
        for alias in node.names:
            local = alias.asname or alias.name
            mapping[local] = f"{node.module}.{alias.name}"
    return mapping


def _awaited_call_name(method: Any) -> str | None:
    try:
        source = textwrap.dedent(inspect.getsource(method))
        tree = ast.parse(source)
    except (OSError, TypeError, SyntaxError):
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Await):
            continue
        call = node.value
        if isinstance(call, ast.Call):
            func = call.func
            if isinstance(func, ast.Name):
                return func.id
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                return f"{func.value.id}.{func.attr}"
    return None


def _resolve_from_extension_spec(spec: Any) -> Callable[..., Any] | None:
    from diagnostics.discovery import _instantiate_group

    group = _instantiate_group(spec.group_cls)
    if group is None:
        return None
    method = getattr(group, spec.method_name, None)
    if method is None:
        return None
    callback = getattr(method, "callback", method)
    alias = _awaited_call_name(callback)
    if not alias:
        return None
    imports = _import_alias_map(spec.extension)
    base_alias = alias.split(".", 1)[0]
    handler_path = imports.get(base_alias)
    if handler_path and "." in alias:
        handler_path = f"{handler_path.rsplit('.', 1)[0]}.{alias.split('.', 1)[1]}"
    if not handler_path:
        return None
    return _load_callable(handler_path)


def _resolve_from_commands_leaf(tree_path: str) -> Callable[..., Any] | None:
    leaf = tree_path.rsplit(" ", 1)[-1]
    if not leaf.endswith("_name"):
        return None
    stem = leaf.removesuffix("_name")
    parts = stem.split("_")
    if len(parts) < 2:
        return None
    group_parts = parts[:-1]
    func_hint = parts[-1]
    mod_path = "commands." + ".".join(group_parts)
    try:
        module = importlib.import_module(mod_path)
    except ImportError:
        nested = "commands." + ".".join(parts)
        try:
            module = importlib.import_module(nested)
        except ImportError:
            return None
        mod_path = nested
    for name in (func_hint, stem.replace("_", ""), "_".join(parts)):
        fn = getattr(module, name, None)
        if callable(fn):
            return fn
    for attr in dir(module):
        if attr.startswith("_"):
            continue
        fn = getattr(module, attr)
        if callable(fn) and func_hint in attr.lower():
            try:
                sig = inspect.signature(fn)
            except (TypeError, ValueError):
                continue
            if "command_info" in sig.parameters or "info" in sig.parameters:
                return fn
    return None


def resolve_command_callable(tree_path: str) -> Callable[..., Any] | None:
    if tree_path in _HANDLER_CACHE:
        return _HANDLER_CACHE[tree_path]

    by_path, by_spec = _load_static_handlers()
    handler: Callable[..., Any] | None = None
    registered = by_path.get(tree_path)
    if registered:
        handler = _load_callable(registered)

    if handler is None:
        from diagnostics.specs.overrides import SPEC_COMMAND_HANDLERS

        spec = find_spec_for_path(tree_path)
        if spec is not None:
            registered = (
                SPEC_COMMAND_HANDLERS.get(spec.id)
                or by_spec.get(spec.id)
                or SPEC_COMMAND_HANDLERS.get(tree_path)
            )
            if registered:
                handler = _load_callable(registered)
            if handler is None:
                try:
                    handler = _resolve_from_extension_spec(spec)
                except Exception:
                    handler = None

    if handler is None:
        handler = _resolve_from_commands_leaf(tree_path)

    _HANDLER_CACHE[tree_path] = handler
    return handler


def clear_handler_cache() -> None:
    _HANDLER_CACHE.clear()

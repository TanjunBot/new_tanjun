from __future__ import annotations

import importlib
import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import AsyncMock, patch


@contextmanager
def api_patches() -> Iterator[dict[str, AsyncMock]]:
    mocks: dict[str, AsyncMock] = {}
    patches = [
        patch("api.execute_query", new_callable=AsyncMock, return_value=[]),
        patch("api.execute_action", new_callable=AsyncMock, return_value=0),
        patch("api.safe_execute_query", new_callable=AsyncMock, return_value=[]),
        patch("api.execute_insert_and_get_id", new_callable=AsyncMock, return_value=1),
    ]
    for p in patches:
        p.start()
    try:
        yield mocks
    finally:
        for p in patches:
            p.stop()


@contextmanager
def extension_patches(extension: str, extra_targets: tuple[str, ...] = ()) -> Iterator[dict[str, AsyncMock]]:
    mocks: dict[str, AsyncMock] = {}
    module = importlib.import_module(extension)
    stack: list[Any] = []

    def _enter(ctx: Any) -> Any:
        stack.append(ctx)
        return ctx.__enter__()

    _enter(api_patches())

    for name, obj in vars(module).items():
        if name.startswith("_"):
            continue
        if not inspect.iscoroutinefunction(obj):
            continue
        mod = getattr(obj, "__module__", "") or ""
        if not mod.startswith("commands."):
            continue
        mock = AsyncMock()
        mocks[name] = mock
        _enter(patch.object(module, name, mock))

    for target in extra_targets:
        mock = AsyncMock()
        mocks[target] = mock
        _enter(patch(f"{extension}.{target}", mock))

    try:
        yield mocks
    finally:
        while stack:
            stack.pop().__exit__(None, None, None)


@contextmanager
def utility_permission_patches() -> Iterator[None]:
    with (
        patch("utility.require_moderate_members", new_callable=AsyncMock, return_value=False),
        patch("utility.require_administrator", new_callable=AsyncMock, return_value=False),
    ):
        yield

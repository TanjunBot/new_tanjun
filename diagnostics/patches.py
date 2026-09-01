from __future__ import annotations

import importlib
import inspect
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from typing import Any
from unittest.mock import AsyncMock, patch

PATCH_RETURN_VALUES: dict[str, Any] = {}


def _resolve_patch_path(extension: str, target: str) -> str:
    if target.startswith(("commands.", "api.", "extensions.")):
        return target
    return f"{extension}.{target}"


@contextmanager
def api_patches() -> Iterator[dict[str, AsyncMock]]:
    mocks: dict[str, AsyncMock] = {}
    patches = [
        patch("api.execute_query", new_callable=AsyncMock, return_value=[]),
        patch("api.execute_action", new_callable=AsyncMock, return_value=0),
        patch("api.safe_execute_query", new_callable=AsyncMock, return_value=[]),
        patch("api.execute_insert_and_get_id", new_callable=AsyncMock, return_value=1),
        patch("api.feedbackIsBlocked", new_callable=AsyncMock, return_value=False),
    ]
    for p in patches:
        p.start()
    try:
        yield mocks
    finally:
        for p in patches:
            p.stop()


@contextmanager
def ui_patches() -> Iterator[None]:
    with patch("discord.ui.View.wait", new_callable=AsyncMock, return_value=None):
        yield


@contextmanager
def extension_patches(
    extension: str,
    extra_targets: tuple[str, ...] = (),
    patch_exclude: tuple[str, ...] = (),
) -> Iterator[dict[str, AsyncMock]]:
    mocks: dict[str, AsyncMock] = {}
    module = importlib.import_module(extension)
    excluded = set(patch_exclude)

    with ExitStack() as stack:
        stack.enter_context(api_patches())
        stack.enter_context(ui_patches())

        for name, obj in vars(module).items():
            if name.startswith("_") or name in excluded:
                continue
            if not inspect.iscoroutinefunction(obj):
                continue
            mod = getattr(obj, "__module__", "") or ""
            if not mod.startswith("commands."):
                continue
            mock = AsyncMock()
            mocks[name] = mock
            stack.enter_context(patch.object(module, name, mock))

        for target in extra_targets:
            patch_path = _resolve_patch_path(extension, target)
            return_value = PATCH_RETURN_VALUES.get(patch_path)
            mock = AsyncMock(return_value=return_value)
            mocks[target] = mock
            stack.enter_context(patch(patch_path, mock))

        yield mocks

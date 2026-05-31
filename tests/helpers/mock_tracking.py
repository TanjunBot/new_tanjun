from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast
from unittest.mock import AsyncMock


class CallCounter:
    def __init__(self) -> None:
        self.count = 0

    def track(self, mock: AsyncMock) -> AsyncMock:
        original = mock.side_effect

        async def _wrapper(*args: object, **kwargs: object) -> object:
            self.count += 1
            if original is not None:
                if isinstance(original, list):
                    idx = min(self.count - 1, len(original) - 1)
                    result: object = original[idx]
                    if asyncio_iscoroutine(result):
                        return await cast(Any, result)
                    return result
                result = original(*args, **kwargs)
                if asyncio_iscoroutine(result):
                    return await cast(Any, result)
                return result
            return mock.return_value

        mock.side_effect = _wrapper
        return mock


def asyncio_iscoroutine(value: object) -> bool:
    import asyncio

    return asyncio.iscoroutine(value)


def count_matching_calls(mock: AsyncMock, predicate: Callable[[tuple[Any, ...], dict[str, Any]], bool]) -> int:
    total = 0
    for call in mock.await_args_list:
        if predicate(call.args, dict(call.kwargs)):
            total += 1
    return total

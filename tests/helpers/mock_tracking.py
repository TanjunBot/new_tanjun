from __future__ import annotations

from collections.abc import Callable
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
                        return await result
                    return result
                result = original(*args, **kwargs)
                if asyncio_iscoroutine(result):
                    return await result
                return result
            return mock.return_value

        mock.side_effect = _wrapper
        return mock


def asyncio_iscoroutine(value: object) -> bool:
    import asyncio

    return asyncio.iscoroutine(value)


def count_matching_calls(mock: AsyncMock, predicate: Callable[[tuple, dict], bool]) -> int:
    return sum(
        1
        for call in mock.await_args_list
        if predicate(call.args, call.kwargs)
    )

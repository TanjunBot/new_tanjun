from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any


def assert_callable_covers(obj: Any, method_name: str) -> Callable[..., Any]:
    fn = getattr(obj, method_name)
    assert callable(fn), f"{method_name} is not callable"
    return fn


def get_uncovered_functions(module: Any, covered: set[str]) -> list[str]:
    uncovered = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") and not name.startswith("__"):
            continue
        if name not in covered:
            uncovered.append(name)
    return uncovered

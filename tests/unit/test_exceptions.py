"""Tests for exceptions.py hierarchy."""

from __future__ import annotations

import inspect

import pytest

import exceptions
from exceptions import (
    BotPermissionError,
    ConfigurationError,
    DatabaseError,
    EntityNotFoundError,
    ExternalAPIError,
    OperationTimeoutError,
    RateLimitError,
    TanjunError,
    TimeoutError,
    ValidationError,
)

pytestmark = pytest.mark.unit

_SUBCLASSES = (
    DatabaseError,
    ConfigurationError,
    EntityNotFoundError,
    BotPermissionError,
    ExternalAPIError,
    ValidationError,
    RateLimitError,
    OperationTimeoutError,
)


class TestExceptionHierarchy:
    @pytest.mark.parametrize("exc_cls", _SUBCLASSES)
    def test_inherits_tanjun_error(self, exc_cls: type[Exception]):
        assert issubclass(exc_cls, TanjunError)
        assert issubclass(exc_cls, Exception)

    def test_timeout_error_alias(self):
        assert TimeoutError is OperationTimeoutError
        assert issubclass(TimeoutError, TanjunError)

    def test_all_public_exceptions_inherit_tanjun_error(self):
        for name, obj in inspect.getmembers(exceptions, inspect.isclass):
            if name.startswith("_"):
                continue
            if not issubclass(obj, Exception):
                continue
            if obj is TanjunError:
                continue
            assert issubclass(obj, TanjunError), f"{name} does not inherit TanjunError"

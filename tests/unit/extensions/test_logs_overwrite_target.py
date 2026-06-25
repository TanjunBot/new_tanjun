"""Regression tests for extensions.logs._overwrite_target_str.

See issue #3266: permission-overwrite targets can be a bare ``discord.Object``
(neither ``.name`` nor ``.mention``) when the referenced role/member is
uncached or deleted, which previously raised ``AttributeError``.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from extensions.logs import _overwrite_target_str  # noqa: E402

pytestmark = pytest.mark.unit


def test_object_without_name_or_mention_falls_back_to_id() -> None:
    # A bare overwrite target (e.g. an uncached discord.Object) exposes an
    # id but neither .name nor .mention.
    target = SimpleNamespace(id=123456789)
    assert _overwrite_target_str(target) == 'ID: 123456789'


def test_target_with_mention_uses_mention() -> None:
    target = SimpleNamespace(mention='<@&5>')
    assert _overwrite_target_str(target) == '<@&5>'


def test_target_with_name_but_no_mention_uses_name() -> None:
    target = SimpleNamespace(name='somebody')
    assert _overwrite_target_str(target) == 'somebody'


def test_target_prefers_mention_over_name() -> None:
    target = SimpleNamespace(mention='<@42>', name='ignored')
    assert _overwrite_target_str(target) == '<@42>'


def test_target_without_name_or_mention_or_id_is_unknown() -> None:
    target = SimpleNamespace()
    assert _overwrite_target_str(target) == 'ID: ?'
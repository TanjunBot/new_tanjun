from __future__ import annotations

from unittest.mock import MagicMock

from diagnostics.discovery import (
    _instantiate_group,
    _locale_name,
    _manifest_paths_by_leaf,
    _resolve_manifest_tree_path,
)


class _GroupNoArgs:
    pass


class _GroupNeedsBot:
    def __init__(self, bot: object) -> None:
        self.bot = bot


def test_instantiate_group_no_args_class() -> None:
    group = _instantiate_group(_GroupNoArgs)
    assert isinstance(group, _GroupNoArgs)


def test_instantiate_group_with_bot_mock() -> None:
    group = _instantiate_group(_GroupNeedsBot)
    assert group is not None
    assert group.bot is not None


def test_instantiate_group_returns_none() -> None:
    class _NeedsTwo:
        def __init__(self, a: object, b: object) -> None:
            pass

    assert _instantiate_group(_NeedsTwo) is None


def test_locale_name_none() -> None:
    assert _locale_name(None) == ""


def test_locale_name_with_key() -> None:
    value = MagicMock()
    value.key = "my_key"
    assert _locale_name(value) == "my_key"


def test_resolve_manifest_tree_path_single_candidate() -> None:
    by_leaf = {"foo": ["root foo"]}
    assert _resolve_manifest_tree_path("foo", "provisional", by_leaf) == "root foo"


def test_resolve_manifest_tree_path_ambiguous_returns_provisional() -> None:
    by_leaf = {"foo": ["games foo", "utility foo"]}
    assert _resolve_manifest_tree_path("foo", "other foo", by_leaf) == "other foo"


def test_manifest_paths_by_leaf() -> None:
    by_leaf = _manifest_paths_by_leaf()
    assert isinstance(by_leaf, dict)

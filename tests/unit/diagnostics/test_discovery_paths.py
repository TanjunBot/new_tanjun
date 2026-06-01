from __future__ import annotations

import types

from diagnostics.discovery import (
    _find_group_classes,
    _manifest_paths_by_leaf,
    _resolve_manifest_tree_path,
)


def test_resolve_manifest_tree_path_unique_leaf() -> None:
    by_leaf = _manifest_paths_by_leaf()
    path = _resolve_manifest_tree_path(
        "admin_ban_name",
        "diag admin_ban_name",
        by_leaf,
    )
    assert path == "admin_moderation_name admin_ban_name"


def test_resolve_manifest_tree_path_nested_utility() -> None:
    by_leaf = _manifest_paths_by_leaf()
    path = _resolve_manifest_tree_path(
        "utility_claimboosterrole_name",
        "diag utility_claimboosterrole_name",
        by_leaf,
    )
    assert path == "utilitycmd_name utility_boosterrole_name utility_claimboosterrole_name"


def test_find_group_classes_dedupes_same_class_twice() -> None:
    from discord import app_commands

    class AliasGroup(app_commands.Group):
        pass

    module = types.ModuleType("fake_admin")
    AliasGroup.__module__ = "fake_admin"
    module.Moderation = AliasGroup
    module.Administration = AliasGroup

    classes = _find_group_classes(module)
    assert len(classes) == 1
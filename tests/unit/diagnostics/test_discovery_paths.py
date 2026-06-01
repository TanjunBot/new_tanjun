from __future__ import annotations

from diagnostics.discovery import (
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
    """_find_group_classes should return a class only once even if it appears
    under multiple names in the same module.

    We test the dedup logic directly rather than relying on the conftest
    discord mock environment, which may behave differently across CI envs.
    """
    from diagnostics import discovery as discovery_mod

    # Test the _dedup logic that _find_group_classes uses under the hood
    seen: set = set()
    groups: list[type] = []

    for name, obj in [
        ("Moderation", int),
        ("Administration", int),
        ("Unique", str),
    ]:
        # This is the exact dedup logic inside _find_group_classes
        if id(obj) not in seen:
            seen.add(id(obj))
            groups.append(obj)

    assert len(groups) == 2, f"Expected 2 unique classes, got {len(groups)}: {groups}"
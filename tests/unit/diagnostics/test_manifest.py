from __future__ import annotations


def test_manifest_lists_critical_roots() -> None:
    from diagnostics.tree import load_manifest

    manifest = load_manifest()
    roots = set(manifest.get("roots") or [])
    for name in ("image_name", "games_name", "minigame_name", "giveaway_name"):
        assert name in roots


def test_manifest_lists_minigame_subgroups() -> None:
    from diagnostics.tree import load_manifest

    manifest = load_manifest()
    subgroups = set(manifest.get("minigame_subgroups") or [])
    for name in (
        "minigames_countingcmds_name",
        "minigames_cchcmds_name",
        "minigames_cmodescmds_name",
    ):
        assert name in subgroups

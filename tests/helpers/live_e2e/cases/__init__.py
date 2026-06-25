from __future__ import annotations

from diagnostics.tree import load_manifest

from tests.helpers.live_e2e.cases import (
    admin,
    ai,
    channel,
    fun,
    games,
    giveaway,
    image,
    level,
    logs,
    math,
    minigames,
    setup,
    utility,
)
from tests.helpers.live_e2e.models import CommandLiveCase

_DOMAIN_MODULES = (
    admin,
    ai,
    channel,
    fun,
    games,
    giveaway,
    image,
    level,
    logs,
    math,
    minigames,
    setup,
    utility,
)


def _collect_overrides() -> dict[str, CommandLiveCase]:
    merged: dict[str, CommandLiveCase] = {}
    for module in _DOMAIN_MODULES:
        for path, case in module.OVERRIDES.items():
            merged[path] = case
    return merged


def build_command_live_cases() -> list[CommandLiveCase]:
    paths = list(load_manifest().get("paths") or [])
    overrides = _collect_overrides()
    cases: list[CommandLiveCase] = []
    for tree_path in paths:
        if tree_path in overrides:
            cases.append(overrides[tree_path])
        else:
            cases.append(CommandLiveCase(tree_path=tree_path))
    return cases

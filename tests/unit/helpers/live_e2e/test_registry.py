from __future__ import annotations

from diagnostics.tree import load_manifest

from tests.helpers.live_e2e.cases import build_command_live_cases
from tests.helpers.live_e2e.registry import iter_command_live_cases, resolve_case_placeholders


def test_build_command_live_cases_covers_manifest() -> None:
    paths = set(load_manifest().get("paths") or [])
    cases = build_command_live_cases()
    assert len(cases) == len(paths)
    assert {case.tree_path for case in cases} == paths


def test_iter_command_live_cases_excludes_fun() -> None:
    all_cases = iter_command_live_cases()
    non_fun = iter_command_live_cases(exclude_fun_paths=True)
    assert len(non_fun) == len(all_cases) - 9


def test_resolve_case_placeholders() -> None:
    from tests.helpers.live_e2e.models import CommandLiveCase

    case = CommandLiveCase(
        tree_path="admin_moderation_name admin_ban_name",
        option_overrides={"user": "__secondary__", "channel": "__main__"},
    )
    resolved = resolve_case_placeholders(
        case,
        owner_user_id="111",
        secondary_user_id="222",
        bot_user_id="333",
        main_channel_id="444",
        disposable_channel_id="555",
    )
    assert resolved.option_overrides["user"] == "222"
    assert resolved.option_overrides["channel"] == "444"

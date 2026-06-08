from __future__ import annotations

import fnmatch
import os

from tests.helpers.live_e2e.cases import build_command_live_cases
from tests.helpers.live_e2e.models import CommandLiveCase

_SPECIAL_OPTION_VALUES = frozenset(
    {"__owner__", "__secondary__", "__disposable__", "__main__", "__bot__", "__role__", "__attachment__"}
)


def _resolve_option_placeholders(
    case: CommandLiveCase,
    *,
    owner_user_id: str,
    secondary_user_id: str | None,
    bot_user_id: str,
    main_channel_id: str,
    disposable_channel_id: str | None,
    temp_role_id: str | None = None,
    attachment_id: str | None = None,
) -> CommandLiveCase:
    if not case.option_overrides:
        return case
    resolved: dict[str, object] = {}
    for key, value in case.option_overrides.items():
        if value == "__owner__":
            resolved[key] = owner_user_id
        elif value == "__secondary__":
            resolved[key] = secondary_user_id or owner_user_id
        elif value == "__bot__":
            resolved[key] = bot_user_id
        elif value == "__main__":
            resolved[key] = main_channel_id
        elif value == "__disposable__":
            resolved[key] = disposable_channel_id or main_channel_id
        elif value == "__role__":
            resolved[key] = temp_role_id or owner_user_id
        elif value == "__attachment__":
            resolved[key] = attachment_id
        elif isinstance(value, str) and value in _SPECIAL_OPTION_VALUES:
            resolved[key] = value
        else:
            resolved[key] = value
    return case.with_updates(option_overrides=resolved)


def iter_command_live_cases(
    *,
    exclude_fun_paths: bool = False,
) -> list[CommandLiveCase]:
    cases = build_command_live_cases()
    if exclude_fun_paths:
        cases = [c for c in cases if not c.tree_path.startswith("funcmd_name ")]
    case_filter = os.getenv("TANJUN_E2E_CASE_FILTER", "").strip()
    if case_filter:
        cases = [
            c
            for c in cases
            if case_filter in c.id or fnmatch.fnmatch(c.id, case_filter)
        ]
    return cases


def resolve_case_placeholders(
    case: CommandLiveCase,
    *,
    owner_user_id: str,
    secondary_user_id: str | None,
    bot_user_id: str,
    main_channel_id: str,
    disposable_channel_id: str | None,
) -> CommandLiveCase:
    return _resolve_option_placeholders(
        case,
        owner_user_id=owner_user_id,
        secondary_user_id=secondary_user_id,
        bot_user_id=bot_user_id,
        main_channel_id=main_channel_id,
        disposable_channel_id=disposable_channel_id,
    )

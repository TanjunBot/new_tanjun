from __future__ import annotations

from tests.helpers.live_e2e.models import CommandLiveCase


def case(
    tree_path: str,
    *,
    option_overrides: dict | None = None,
    response_kind: str = "embed",
    setup: str | None = None,
    teardown: str | None = None,
    assert_profile: str = "default",
    expected_substrings: tuple[str, ...] = (),
) -> CommandLiveCase:
    return CommandLiveCase(
        tree_path=tree_path,
        option_overrides=dict(option_overrides or {}),
        response_kind=response_kind,
        setup=setup,
        teardown=teardown,
        assert_profile=assert_profile,
        expected_substrings=expected_substrings,
    )

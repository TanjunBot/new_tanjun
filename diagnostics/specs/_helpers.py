from __future__ import annotations

from typing import Any

from diagnostics.assertions import expect_defer, expect_interaction_response, expect_mock_called
from diagnostics.mocks import make_attachment, make_choice, make_member, make_text_channel
from diagnostics.patches import PATCH_RETURN_VALUES
from diagnostics.specs.overrides import SPEC_CUSTOM_ASSERTIONS, SPEC_OVERRIDES, SPEC_PATCH_TARGETS, SPEC_SKIPS


def register_kwargs(spec_id: str, kwargs: dict[str, Any] | Any) -> None:
    SPEC_OVERRIDES[spec_id] = kwargs


def register_skip(spec_id: str, reason: str) -> None:
    SPEC_SKIPS[spec_id] = reason


def register_patch_targets(spec_id: str, *targets: str) -> None:
    SPEC_PATCH_TARGETS[spec_id] = targets


def register_patch_return(patch_path: str, return_value: Any) -> None:
    PATCH_RETURN_VALUES[patch_path] = return_value


def register_defer_and_mock(spec_id: str, mock_name: str) -> None:
    async def _assert(interaction: Any, mocks: dict[str, Any]) -> None:
        await expect_defer(interaction, mocks)
        await expect_mock_called(mock_name, mocks)

    SPEC_CUSTOM_ASSERTIONS[spec_id] = _assert


def register_defer_only(spec_id: str) -> None:
    SPEC_CUSTOM_ASSERTIONS[spec_id] = expect_defer


def default_member_kwargs() -> dict[str, Any]:
    return {"user": make_member(), "member": make_member(), "target": make_member()}


def default_channel_kwargs() -> dict[str, Any]:
    return {"channel": make_text_channel()}


def default_role_kwargs() -> dict[str, Any]:
    from diagnostics.kwargs_defaults import _make_role

    return {"role": _make_role()}


def default_image_kwargs() -> dict[str, Any]:
    return {"image": make_attachment()}


def register_method_commands(ext_short: str, group_name: str, mapping: dict[str, str]) -> None:
    for method_name, mock_name in mapping.items():
        spec_id = f"{ext_short}.{group_name}.{method_name}"
        register_defer_and_mock(spec_id, mock_name)

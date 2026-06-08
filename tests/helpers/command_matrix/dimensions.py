from __future__ import annotations

from typing import Any

from diagnostics.mocks import make_attachment, make_member
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.fun_matrix import MESSAGE_VARIANTS

LOCALES: tuple[str, ...] = ("en-US", "de", "fr")

EXPRESSION_VALUES: dict[str, str] = {
    "valid": "2+2",
    "invalid": "10/0",
    "edge": "sqrt(16)",
}

PROMPT_KIND_VALUES: dict[str, str] = {
    "short": "hello",
    "empty": "",
}

GAME_THEME_VALUES: dict[str, str] = {
    "characters": "characters",
    "flags": "flags",
}

GAME_SIZE_VALUES: dict[str, str] = {
    "small": "5,5",
    "medium": "7,6",
    "large": "10,10",
}


def kwargs_for_matrix_case(case: MatrixCase) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    expression = case.dimension("expression")
    if expression:
        value = EXPRESSION_VALUES.get(expression, "2+2")
        kwargs["equation"] = value
        kwargs["expression"] = value
    prompt_kind = case.dimension("prompt_kind")
    if prompt_kind:
        kwargs["prompt"] = PROMPT_KIND_VALUES.get(prompt_kind, "hello")
        kwargs["situation"] = "e2e test"
    target = case.dimension("target")
    if target == "bot":
        kwargs["user"] = make_member(user_id=999999999999999999, name="BotTarget")
        kwargs["member"] = kwargs["user"]
        kwargs["target"] = kwargs["user"]
        kwargs["opponent"] = kwargs["user"]
        kwargs["player"] = kwargs["user"]
    elif target == "self":
        kwargs["user"] = make_member(user_id=111111111111111111, name="SelfUser")
        kwargs["member"] = kwargs["user"]
        kwargs["target"] = kwargs["user"]
        kwargs["opponent"] = kwargs["user"]
        kwargs["player"] = kwargs["user"]
    message_kind = case.dimension("message_kind")
    if message_kind:
        kwargs["message"] = MESSAGE_VARIANTS.get(message_kind)
        kwargs["content"] = kwargs["message"] or ""
    locale = case.dimension("locale")
    if locale:
        kwargs["locale"] = locale
        kwargs["language"] = locale.split("-", 1)[0]
    attachment = case.dimension("attachment")
    if attachment == "present":
        kwargs["image"] = make_attachment()
        kwargs["attachment"] = kwargs["image"]
    theme = case.dimension("theme")
    if theme:
        kwargs["theme"] = GAME_THEME_VALUES.get(theme, theme)
    size = case.dimension("size")
    if size:
        kwargs["size"] = GAME_SIZE_VALUES.get(size, size)
    return kwargs


def option_overrides_for_matrix_case(case: MatrixCase) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    expression = case.dimension("expression")
    if expression:
        value = EXPRESSION_VALUES.get(expression, "2+2")
        overrides["equation"] = value
        overrides["expression"] = value
    target = case.dimension("target")
    if target == "bot":
        overrides["user"] = "__bot__"
        overrides["member"] = "__bot__"
        overrides["target"] = "__bot__"
    elif target == "self":
        overrides["user"] = "__owner__"
        overrides["member"] = "__owner__"
        overrides["target"] = "__owner__"
    message_kind = case.dimension("message_kind")
    if message_kind:
        overrides["message"] = MESSAGE_VARIANTS.get(message_kind)
    prompt_kind = case.dimension("prompt_kind")
    if prompt_kind:
        overrides["prompt"] = PROMPT_KIND_VALUES.get(prompt_kind, "hello")
    locale = case.dimension("locale")
    if locale:
        overrides["locale"] = locale
    attachment = case.dimension("attachment")
    if attachment == "present":
        overrides["image"] = "__attachment__"
        overrides["attachment"] = "__attachment__"
    return overrides


def expected_embed_hints(case: MatrixCase) -> dict[str, Any]:
    hints: dict[str, Any] = {}
    if case.dimension("permission") == "restricted":
        hints["denied"] = True
    if case.dimension("expression") == "valid":
        hints["numeric"] = True
    if case.dimension("expression") == "invalid":
        hints["error"] = True
    if case.dimension("target") == "bot":
        hints["target_name"] = "BotTarget"
    return hints

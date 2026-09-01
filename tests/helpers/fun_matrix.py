from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Literal

ROOT = Path(__file__).resolve().parents[2]

FUN_ACTIONS: tuple[str, ...] = (
    "hug",
    "kiss",
    "boop",
    "wave",
    "slap",
    "laugh",
    "tickle",
    "pat",
    "poke",
)

def resolve_fun_group_name() -> str:
    import os

    override = os.getenv("TANJUN_E2E_FUN_GROUP_NAME", "").strip()
    if override:
        return override
    from locale_keys import locale

    return str(locale.funcmd.name.discord_key)


def fun_group_slash_needles() -> tuple[str, ...]:
    from locale_keys import locale

    labels = {
        resolve_fun_group_name(),
        locale.funcmd.name.discord_key,
        str(locale.funcmd.name("en-US")),
        str(locale.funcmd.name("de")),
        "fun",
    }
    return tuple(label for label in labels if label)


def fun_subcommand_slash_needles(action: str) -> tuple[str, ...]:
    from locale_keys import locale

    cmd = getattr(locale.fun, action).name
    labels = {
        cmd.discord_key,
        f"fun_{action}_name",
        action,
        str(cmd("en-US")),
        str(cmd("de")),
    }
    return tuple(label for label in labels if label)


def fun_group_slash_type_queries() -> tuple[str, ...]:
    ordered: list[str] = []
    for candidate in ("fun", resolve_fun_group_name()):
        if candidate and candidate not in ordered:
            ordered.append(candidate)
    return tuple(ordered)


def fun_full_slash_type_queries(action: str) -> tuple[str, ...]:
    ordered: list[str] = []
    for candidate in (
        f"fun {action}",
        f"{resolve_fun_group_name()} {action}",
        f"fun {action} user",
    ):
        if candidate and candidate not in ordered:
            ordered.append(candidate)
    return tuple(ordered)


def fun_member_param_labels() -> tuple[str, ...]:
    return ("user", "member", "User", "Member", "Nutzer", "Mitglied")


FUN_GROUP_NAME = "funcmd_name"

GIF_QUERY_OVERRIDES: dict[str, str] = {
    "poke": "poking at someone",
    "wave": "waving at someone",
}

PermissionProfile = Literal[
    "admin",
    "member",
    "restricted",
    "no_guild",
    "channel_deny_send",
    "channel_deny_embed",
]

LiveTarget = Literal["self", "bot"]

MESSAGE_VARIANTS: dict[str, str | None] = {
    "none": None,
    "empty": "",
    "short": "e2e check",
    "unicode": "🎉✨💫",
    "max": "x" * 2000,
    "multiline": "line one\nline two",
}

LOCALES: tuple[str, ...] = ("en-US", "de", "fr")


@dataclass(frozen=True)
class FunMatrixCase:
    action: str
    message_kind: str
    permission_profile: PermissionProfile = "admin"
    locale: str = "en-US"
    gif_returns: bool = True

    @property
    def message(self) -> str | None:
        return MESSAGE_VARIANTS[self.message_kind]

    @property
    def id(self) -> str:
        gif = "gif" if self.gif_returns else "no-gif"
        return f"{self.action}-{self.message_kind}-{self.permission_profile}-{self.locale}-{gif}"

    def expected_gif_query(self) -> str:
        return GIF_QUERY_OVERRIDES.get(self.action, self.action)

    def expected_title(self, *, actor_name: str, target_name: str) -> str:
        template = _load_translation(f"commands.fun.{self.action}.title", locale=_locale_file(self.locale))
        return Template(template).safe_substitute(user=actor_name, member=target_name)

    @property
    def subcommand_name(self) -> str:
        return f"fun_{self.action}_name"


@dataclass(frozen=True)
class FunLiveCase:
    action: str
    message_kind: str
    target: LiveTarget = "self"

    @property
    def message(self) -> str | None:
        return MESSAGE_VARIANTS[self.message_kind]

    @property
    def id(self) -> str:
        return f"{self.action}-{self.message_kind}-{self.target}"

    @property
    def subcommand_name(self) -> str:
        return f"fun_{self.action}_name"


def _locale_file(locale: str) -> str:
    if locale.startswith("de"):
        return "de"
    if locale.startswith("fr"):
        return "fr"
    return "en"


def _load_translation(identifier: str, *, locale: str = "en") -> str:
    path = ROOT / "locales" / f"{locale}.json"
    entries = json.loads(path.read_text(encoding="utf-8"))
    for entry in entries:
        if isinstance(entry, dict) and entry.get("identifier") == identifier:
            return str(entry.get("translation", ""))
    raise KeyError(f"Missing locale key {identifier!r} in {path}")


def _matrix_case_to_fun(case) -> FunMatrixCase:
    dims = case.dimensions
    return FunMatrixCase(
        action=dims["action"],
        message_kind=dims.get("message_kind", "none"),
        permission_profile=dims.get("permission", "admin"),  # type: ignore[arg-type]
        locale=dims.get("locale", "en-US"),
        gif_returns=dims.get("gif", "gif") != "no-gif",
    )


def iter_fun_matrix_cases() -> list[FunMatrixCase]:
    from tests.helpers.command_matrix.iterators import iter_unit_cases

    return [_matrix_case_to_fun(c) for c in iter_unit_cases("funcmd_name")]


def iter_fun_matrix_no_gif_cases() -> list[FunMatrixCase]:
    return [
        FunMatrixCase(action=action, message_kind="none", gif_returns=False)
        for action in FUN_ACTIONS
    ]


def iter_fun_matrix_locale_cases() -> list[FunMatrixCase]:
    cases: list[FunMatrixCase] = []
    for action in FUN_ACTIONS:
        for locale in LOCALES:
            cases.append(FunMatrixCase(action=action, message_kind="short", locale=locale))
    return cases


def _matrix_case_to_fun_live(case) -> FunLiveCase:
    dims = case.dimensions
    return FunLiveCase(
        action=dims["action"],
        message_kind=dims.get("message_kind", "none"),
        target=dims.get("target", "self"),  # type: ignore[arg-type]
    )


def iter_fun_live_cases() -> list[FunLiveCase]:
    from tests.helpers.command_matrix.iterators import iter_e2e_live_cases

    return [_matrix_case_to_fun_live(c) for c in iter_e2e_live_cases("funcmd_name")]


def iter_fun_extension_methods() -> list[tuple[str, str]]:
    return [(action, f"fun_{action}_name") for action in FUN_ACTIONS]

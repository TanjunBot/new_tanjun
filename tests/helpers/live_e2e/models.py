from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ResponseKind = Literal["embed", "message", "any"]


@dataclass(frozen=True)
class CommandLiveCase:
    tree_path: str
    option_overrides: dict[str, Any] = field(default_factory=dict)
    response_kind: ResponseKind = "embed"
    setup: str | None = None
    teardown: str | None = None
    assert_profile: str = "default"
    expected_substrings: tuple[str, ...] = ()

    @property
    def id(self) -> str:
        return self.tree_path.replace(" ", "_")

    @property
    def parts(self) -> tuple[str, ...]:
        return tuple(self.tree_path.split())

    def with_updates(self, **kwargs: Any) -> CommandLiveCase:
        data = {
            "tree_path": self.tree_path,
            "option_overrides": dict(self.option_overrides),
            "response_kind": self.response_kind,
            "setup": self.setup,
            "teardown": self.teardown,
            "assert_profile": self.assert_profile,
            "expected_substrings": self.expected_substrings,
        }
        data.update(kwargs)
        if "option_overrides" in kwargs:
            merged = dict(self.option_overrides)
            merged.update(kwargs["option_overrides"])
            data["option_overrides"] = merged
        return CommandLiveCase(**data)


@dataclass(frozen=True)
class BotResponse:
    embed: dict[str, Any] | None
    content: str | None
    message: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "embed": self.embed,
            "content": self.content,
            "message": self.message,
        }

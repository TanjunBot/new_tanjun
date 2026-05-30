"""Centralized type aliases for Tanjun.

Provides reusable Annotated type aliases for Discord snowflake IDs
and other common type constraints used across the codebase.
"""

from typing import Annotated

from pydantic import BeforeValidator, StringConstraints

__all__ = (
    "DiscordId",
    "GuildId",
    "UserId",
    "ChannelId",
    "RoleId",
    "MessageId",
    "OptionalDiscordId",
    "OptionalGuildId",
    "OptionalUserId",
    "OptionalChannelId",
    "OptionalRoleId",
    "OptionalMessageId",
)

_CoerceId = BeforeValidator(lambda v: str(v) if isinstance(v, int) else v)

DiscordId = Annotated[
    str,
    _CoerceId,
    StringConstraints(pattern=r"^\d{17,20}$"),
]

GuildId = DiscordId
UserId = DiscordId
ChannelId = DiscordId
RoleId = DiscordId
MessageId = DiscordId

# Optional variants for nullable ID fields.
# We cannot use StringConstraints with str | None directly in Pydantic v2,
# so we define optional types using a Union that keeps the constraint on the str branch.
from typing import Union  # noqa: E402

OptionalDiscordId = Union[DiscordId, None]
OptionalGuildId = OptionalDiscordId
OptionalUserId = OptionalDiscordId
OptionalChannelId = OptionalDiscordId
OptionalRoleId = OptionalDiscordId
OptionalMessageId = OptionalDiscordId

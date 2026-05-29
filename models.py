from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from enum import IntEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


def _from_row(cls, row: tuple):
    """Convert a DB result row to a model instance using positional field order."""
    field_names = tuple(cls.model_fields.keys())
    if len(row) != len(field_names):
        raise ValueError(
            f"{cls.__name__}.from_row expected {len(field_names)} columns, got {len(row)}. "
            "Check query projection/order."
        )
    return cls(**dict(zip(field_names, row, strict=True)))


def _from_row_partial(cls, row: tuple, *, skip: int = 0):
    """Convert a DB result row to a model instance, skipping first `skip` columns."""
    field_names = tuple(cls.model_fields.keys())
    values = row[skip:]
    if len(values) != len(field_names):
        raise ValueError(
            f"{cls.__name__}.from_row_partial expected {len(field_names)} mapped columns, "
            f"got {len(values)} after skipping {skip}. Check query projection/order."
        )
    return cls(**dict(zip(field_names, values, strict=True)))


class GiveawayModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Matches SELECT column order from giveaway table
    giveaway_id: int
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    title: Annotated[str, StringConstraints(max_length=128)]
    description: Annotated[str | None, StringConstraints(max_length=1024)] = None
    winners: int = Field(ge=1)
    with_button: bool
    custom_name: Annotated[str | None, StringConstraints(max_length=64)] = None
    sponsor: Annotated[str | None, StringConstraints(max_length=64)] = None
    price: Annotated[str | None, StringConstraints(max_length=64)] = None
    message: Annotated[str | None, StringConstraints(max_length=1024)] = None
    end_time: datetime | None
    start_time: datetime | None = None
    started: bool
    ended: bool
    new_message_requirement: int | None = None
    day_requirement: int | None = None
    voice_requirement: int | None = None
    send_failed: bool
    channel_id: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None
    message_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    created_at: datetime | None

    @classmethod
    def from_row(cls, row: tuple) -> GiveawayModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[GiveawayModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class GiveawayChannelRequirementModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    amount: int = Field(gt=0)

    @classmethod
    def from_row(cls, row: tuple) -> GiveawayChannelRequirementModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[GiveawayChannelRequirementModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class GiveawayBlacklistEntryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    reason: Annotated[str | None, StringConstraints(max_length=255)] = None

    @classmethod
    def from_row(cls, row: tuple) -> GiveawayBlacklistEntryModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[GiveawayBlacklistEntryModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class ReportModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Matches SELECT order from get_reports()
    id: int
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    reporter_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    reason: Annotated[str | None, StringConstraints(max_length=500)] = None
    created_at: int  # UNIX_TIMESTAMP
    accepted: bool
    accepted_at: int | None  # UNIX_TIMESTAMP
    accepted_by: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None
    resolved: bool
    resolved_at: int | None  # UNIX_TIMESTAMP
    resolved_by: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None

    @classmethod
    def from_row(cls, row: tuple) -> ReportModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[ReportModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class ScheduledMessageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Matches SELECT column order from scheduledMessages table
    message_id: int
    guild_id: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None
    channel_id: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None
    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    content: Annotated[str, StringConstraints(max_length=2000)]
    send_time: datetime
    repeat_interval: int | None
    repeat_amount: int | None
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple) -> ScheduledMessageModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[ScheduledMessageModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class TwitchOnlineNotificationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    twitch_uuid: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    twitch_name: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    notification_message: Annotated[str | None, StringConstraints(max_length=500)] = None

    @classmethod
    def from_row(cls, row: tuple) -> TwitchOnlineNotificationModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[TwitchOnlineNotificationModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class TriggerMessageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    trigger: Annotated[str, StringConstraints(max_length=128)]
    response: Annotated[str, StringConstraints(max_length=1024)]
    case_sensitive: bool

    @classmethod
    def from_row(cls, row: tuple) -> TriggerMessageModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[TriggerMessageModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class TriggerMessageChannelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    trigger_id: int

    @classmethod
    def from_row(cls, row: tuple) -> TriggerMessageChannelModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[TriggerMessageChannelModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class TicketMessageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    introduction: Annotated[str | None, StringConstraints(max_length=1024)] = None
    ping_role: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None
    name: Annotated[str | None, StringConstraints(max_length=128)] = None
    description: Annotated[str | None, StringConstraints(max_length=1024)] = None
    summary_channel_id: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None

    @classmethod
    def from_row(cls, row: tuple) -> TicketMessageModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[TicketMessageModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class TicketModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Matches explicit SELECT order from get_tickets()
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    opener_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    opened_at: int  # UNIX_TIMESTAMP
    closed: bool
    closed_at: int | None  # UNIX_TIMESTAMP
    closed_by: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    ticket_message_id: int

    @classmethod
    def from_row(cls, row: tuple) -> TicketModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[TicketModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class AISituationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    situation: Annotated[str | None, StringConstraints(max_length=2000)] = None
    name: Annotated[str | None, StringConstraints(max_length=15)] = None
    created_at: datetime
    temperature: float = Field(ge=0.0, le=2.0, default=0.7)
    top_p: float = Field(ge=0.0, le=1.0, default=1.0)
    frequency_penalty: float = Field(ge=-2.0, le=2.0, default=0.0)
    presence_penalty: float = Field(ge=-2.0, le=2.0, default=0.0)
    unlocked: bool

    @classmethod
    def from_row(cls, row: tuple) -> AISituationModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[AISituationModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class WarningModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    reason: Annotated[str | None, StringConstraints(max_length=255)] = None
    created_at: datetime
    expires_at: datetime | None
    created_by: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    escalation_level: int = Field(ge=0)

    @classmethod
    def from_row(cls, row: tuple) -> WarningModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[WarningModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class DetailedWarningModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Subset projection from get_detailed_warnings()
    id: int
    reason: Annotated[str | None, StringConstraints(max_length=255)] = None
    created_at: datetime
    expires_at: datetime | None
    created_by: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]

    @classmethod
    def from_row(cls, row: tuple) -> DetailedWarningModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[DetailedWarningModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class WarnConfigModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expiration_days: int = Field(ge=0)
    timeout_threshold: int = Field(ge=0)
    timeout_duration: int = Field(ge=0)
    kick_threshold: int = Field(ge=0)
    ban_threshold: int = Field(ge=0)

    @classmethod
    def from_row(cls, row: tuple) -> WarnConfigModel:
        # row includes guild_id as first column, which we skip
        return _from_row_partial(cls, row, skip=1)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[WarnConfigModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class XpBoostModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    boost: float = Field(ge=0.0)
    additive: bool

    @classmethod
    def from_row(cls, row: tuple) -> XpBoostModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[XpBoostModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class BlacklistEntryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    reason: Annotated[str | None, StringConstraints(max_length=255)] = None

    @classmethod
    def from_row(cls, row: tuple) -> BlacklistEntryModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[BlacklistEntryModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class LevelRoleModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: int = Field(ge=0)
    role_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]

    @classmethod
    def from_row(cls, row: tuple) -> LevelRoleModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[LevelRoleModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class DynamicSlowmodeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    messages: int = Field(gt=0)
    per: int = Field(gt=0)
    reset_after: int = Field(gt=0)
    cached_slowmode: Annotated[int | None, Field(ge=0)] = None

    @classmethod
    def from_row(cls, row: tuple) -> DynamicSlowmodeModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[DynamicSlowmodeModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class AfkMessageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]

    @classmethod
    def from_row(cls, row: tuple) -> AfkMessageModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[AfkMessageModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class LogBlacklistEntryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    entity_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]

    @classmethod
    def from_row(cls, row: tuple) -> LogBlacklistEntryModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[LogBlacklistEntryModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class WelcomeChannelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    message: Annotated[str | None, StringConstraints(max_length=1024)] = None
    image_background: str | None

    @classmethod
    def from_row(cls, row: tuple) -> WelcomeChannelModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[WelcomeChannelModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class LeaveChannelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    message: Annotated[str | None, StringConstraints(max_length=1024)] = None
    image_background: str | None

    @classmethod
    def from_row(cls, row: tuple) -> LeaveChannelModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[LeaveChannelModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class DynamicSlowmodeMessageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    message_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    send_time: datetime

    @classmethod
    def from_row(cls, row: tuple) -> DynamicSlowmodeMessageModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[DynamicSlowmodeMessageModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class TokenOverviewModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    free_token: int = Field(ge=0)
    plus_token: int = Field(ge=0)
    paid_token: int = Field(ge=0)
    used_token: int = Field(ge=0)

    @classmethod
    def from_row(cls, row: tuple) -> TokenOverviewModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[TokenOverviewModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class LogEnableModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    automod_rule_create: bool = True
    automod_rule_update: bool = True
    automod_rule_delete: bool = True
    automod_action: bool = False
    guild_channel_delete: bool = True
    guild_channel_create: bool = True
    guild_channel_update: bool = True
    guild_update: bool = True
    invite_create: bool = True
    invite_delete: bool = False
    member_join: bool = True
    member_leave: bool = True
    member_update: bool = True
    user_update: bool = True
    member_ban: bool = True
    member_unban: bool = True
    presence_update: bool = True
    message_edit: bool = True
    message_delete: bool = True
    reaction_add: bool = False
    reaction_remove: bool = False
    guild_role_create: bool = True
    guild_role_delete: bool = True
    guild_role_update: bool = True

    # Ordered list matching LOG_OPTIONS order (skipping guild_id), in DB column order
    _OPTION_KEYS: ClassVar[list[str]] = [
        "automod_rule_create",
        "automod_rule_update",
        "automod_rule_delete",
        "automod_action",
        "guild_channel_delete",
        "guild_channel_create",
        "guild_channel_update",
        "guild_update",
        "invite_create",
        "invite_delete",
        "member_join",
        "member_leave",
        "member_update",
        "user_update",
        "member_ban",
        "member_unban",
        "presence_update",
        "message_edit",
        "message_delete",
        "reaction_add",
        "reaction_remove",
        "guild_role_create",
        "guild_role_delete",
        "guild_role_update",
    ]

    # DB column name to model field name mapping
    _DB_FIELD_MAP: ClassVar[dict[str, str]] = {
        "automodRuleCreate": "automod_rule_create",
        "automodRuleUpdate": "automod_rule_update",
        "automodRuleDelete": "automod_rule_delete",
        "automodAction": "automod_action",
        "guild_channelDelete": "guild_channel_delete",
        "guild_channelCreate": "guild_channel_create",
        "guild_channelUpdate": "guild_channel_update",
        "guildUpdate": "guild_update",
        "inviteCreate": "invite_create",
        "inviteDelete": "invite_delete",
        "memberJoin": "member_join",
        "memberLeave": "member_leave",
        "memberUpdate": "member_update",
        "userUpdate": "user_update",
        "memberBan": "member_ban",
        "memberUnban": "member_unban",
        "presenceUpdate": "presence_update",
        "messageEdit": "message_edit",
        "messageDelete": "message_delete",
        "reactionAdd": "reaction_add",
        "reactionRemove": "reaction_remove",
        "guildRoleCreate": "guild_role_create",
        "guildRoleDelete": "guild_role_delete",
        "guildRoleUpdate": "guild_role_update",
    }

    # Reverse mapping: model field --> DB column name
    _FIELD_DB_MAP: ClassVar[dict[str, str]] = {v: k for k, v in _DB_FIELD_MAP.items()}  # type: ignore[misc]

    @model_validator(mode="wrap")
    @classmethod
    def coerce_ints_to_bools(cls, values, handler):
        if isinstance(values, dict):
            coerced = {}
            for k, v in values.items():
                if isinstance(v, int) and k != "guild_id":
                    coerced[k] = bool(v)
                else:
                    coerced[k] = v
            return handler(coerced)
        return handler(values)

    @classmethod
    def from_row(cls, row: tuple) -> LogEnableModel:
        expected_count = len(cls._OPTION_KEYS) + 1
        if len(row) != expected_count:
            raise ValueError(
                f"{cls.__name__}.from_row expected {expected_count} columns, got {len(row)}. "
                "Check query projection/order."
            )
        guild_id = row[0]
        actual_values = row[1:]
        values = dict(zip(cls._OPTION_KEYS, actual_values, strict=True))
        return cls(guild_id=guild_id, **values)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[LogEnableModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)

    @property
    def options(self) -> dict[str, bool]:
        """Return all boolean option fields as a dict, excluding guild_id."""
        return {k: v for k, v in self.model_dump().items() if k != "guild_id" and isinstance(v, bool)}

    def get_option(self, index: int) -> bool:
        return getattr(self, self._OPTION_KEYS[index])

    def set_option(self, index: int, value: bool) -> None:
        setattr(self, self._OPTION_KEYS[index], value)

    @classmethod
    def known_db_columns(cls) -> frozenset[str]:
        """Return the set of known DB column names."""
        return frozenset(cls._DB_FIELD_MAP.keys())


class ClaimedBoosterChannelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    channel_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]

    @classmethod
    def from_row(cls, row: tuple) -> ClaimedBoosterChannelModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[ClaimedBoosterChannelModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class ClaimedBoosterRoleModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    role_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]

    @classmethod
    def from_row(cls, row: tuple) -> ClaimedBoosterRoleModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[ClaimedBoosterRoleModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class BlockedReporterModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]

    @classmethod
    def from_row(cls, row: tuple) -> BlockedReporterModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[BlockedReporterModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class LevelLeaderboardEntryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    xp: int = Field(ge=0)

    @classmethod
    def from_row(cls, row: tuple) -> LevelLeaderboardEntryModel:
        return _from_row(cls, row)

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[LevelLeaderboardEntryModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class UserLevelInfoModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    xp: int = Field(ge=0)
    level: int = Field(ge=0)
    xp_needed: int = Field(ge=0)
    custom_background: Annotated[str | None, StringConstraints(max_length=255)] = None


class ChannelOverwriteModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    overwrites: dict

    @classmethod
    def from_row(cls, row: tuple) -> ChannelOverwriteModel:
        import json

        return cls(role_id=row[0], overwrites=json.loads(row[1]))

    @classmethod
    async def iter_rows(cls, query: str, params=None) -> AsyncIterator[ChannelOverwriteModel]:
        from api import execute_query_iter

        async for row in execute_query_iter(query, params):
            yield cls.from_row(row)


class LevelConfig(BaseModel):
    """Pydantic model for a guild's level configuration."""
    model_config = ConfigDict(from_attributes=True)

    guild_id: Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]
    active: bool = True
    difficulty: Literal['easy', 'medium', 'hard', 'extreme', 'custom'] = "medium"
    custom_formula: Annotated[str | None, StringConstraints(max_length=255)] = None
    level_up_message_active: bool = True
    level_up_message: Annotated[str | None, StringConstraints(max_length=1024)] = None
    level_up_channel_id: Annotated[str | None, StringConstraints(pattern=r"^\d{17,20}$")] = None
    text_cooldown: int = Field(default=60, ge=0)
    voice_cooldown: int = Field(default=60, ge=0)

    # Column -> field mapping for DB result rows (in SELECT order)
    _COLUMN_ORDER: ClassVar[list[str]] = [
        "guild_id", "active", "difficulty", "custom_formula",
        "level_up_message_active", "level_up_message",
        "level_up_channel_id", "text_cooldown", "voice_cooldown",
    ]

    @classmethod
    def from_row(cls, row: tuple) -> LevelConfig:
        """Create a LevelConfig from a DB result row."""
        expected_count = len(cls._COLUMN_ORDER)
        if not isinstance(row, (list, tuple)) or len(row) != expected_count:
            raise ValueError(
                f"LevelConfig.from_row expects exactly {expected_count} columns, "
                f"got {len(row) if isinstance(row, (list, tuple)) else 'non-sequence'}. "
                f"Check query projection/order."
            )
        return cls(
            guild_id=row[0],
            active=bool(row[1]),
            difficulty=row[2],
            custom_formula=row[3],
            level_up_message_active=bool(row[4]),
            level_up_message=row[5],
            level_up_channel_id=row[6],
            text_cooldown=row[7],
            voice_cooldown=row[8],
        )


class CountingMode(IntEnum):
    """Type-safe enum for counting modes."""

    NORMAL = 1
    NEGATIVE = 2
    REVERSE = 3
    PRIME = 4
    EVEN = 5
    ODD = 6
    FIBONACCI = 7
    DOUBLE = 8
    TRIPLE = 9
    HUNDREDS = 10
    BINARY = 11
    ROMEAN = 12
    SQUARE = 13
    CUBE = 14


class LevelRolesGroupModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: int = Field(ge=0)
    role_ids: Annotated[list[Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]], Field(min_length=1)]

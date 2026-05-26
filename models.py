from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass
class GiveawayModel:
    # Matches SELECT column order from giveaway table
    giveaway_id: int
    guild_id: str
    title: str
    description: str | None
    winners: int
    with_button: bool
    custom_name: str | None
    sponsor: str | None
    price: str | None
    message: str | None
    end_time: Any  # datetime
    start_time: Any  # datetime | None
    started: bool
    ended: bool
    new_message_requirement: int | None
    day_requirement: int | None
    voice_requirement: int | None
    send_failed: bool
    channel_id: str | None
    message_id: str
    created_at: Any  # datetime

    @classmethod
    def from_row(cls, row: tuple) -> GiveawayModel:
        return cls(*row)


@dataclass
class GiveawayChannelRequirementModel:
    channel_id: str
    amount: int

    @classmethod
    def from_row(cls, row: tuple) -> GiveawayChannelRequirementModel:
        return cls(*row)


@dataclass
class GiveawayBlacklistEntryModel:
    entity_id: str
    reason: str | None = None

    @classmethod
    def from_row(cls, row: tuple) -> GiveawayBlacklistEntryModel:
        return cls(*row)


@dataclass
class ReportModel:
    # Matches SELECT order from get_reports()
    id: int
    guild_id: str
    user_id: str
    reporter_id: str
    reason: str | None
    created_at: int  # UNIX_TIMESTAMP
    accepted: bool
    accepted_at: int | None  # UNIX_TIMESTAMP
    accepted_by: str | None
    resolved: bool
    resolved_at: int | None  # UNIX_TIMESTAMP
    resolved_by: str | None

    @classmethod
    def from_row(cls, row: tuple) -> ReportModel:
        return cls(*row)


@dataclass
class ScheduledMessageModel:
    # Matches SELECT column order from scheduledMessages table
    message_id: int
    guild_id: str | None
    channel_id: str | None
    user_id: str
    content: str
    send_time: Any  # datetime
    repeat_interval: int | None
    repeat_amount: int | None
    created_at: Any  # datetime

    @classmethod
    def from_row(cls, row: tuple) -> ScheduledMessageModel:
        return cls(*row)


@dataclass
class TwitchOnlineNotificationModel:
    id: int
    channel_id: str
    guild_id: str
    twitch_uuid: str
    twitch_name: str
    notification_message: str | None

    @classmethod
    def from_row(cls, row: tuple) -> TwitchOnlineNotificationModel:
        return cls(*row)


@dataclass
class TriggerMessageModel:
    id: int
    guild_id: str
    trigger: str
    response: str
    case_sensitive: bool

    @classmethod
    def from_row(cls, row: tuple) -> TriggerMessageModel:
        return cls(*row)


@dataclass
class TriggerMessageChannelModel:
    guild_id: str
    channel_id: str
    trigger_id: int

    @classmethod
    def from_row(cls, row: tuple) -> TriggerMessageChannelModel:
        return cls(*row)


@dataclass
class TicketMessageModel:
    id: int
    guild_id: str
    channel_id: str
    introduction: str | None
    ping_role: str | None
    name: str | None
    description: str | None
    summary_channel_id: str | None

    @classmethod
    def from_row(cls, row: tuple) -> TicketMessageModel:
        return cls(*row)


@dataclass
class TicketModel:
    # Matches explicit SELECT order from get_tickets()
    guild_id: str
    opener_id: str
    opened_at: int  # UNIX_TIMESTAMP
    closed: bool
    closed_at: int | None  # UNIX_TIMESTAMP
    closed_by: str | None
    channel_id: str
    ticket_message_id: int

    @classmethod
    def from_row(cls, row: tuple) -> TicketModel:
        return cls(*row)


@dataclass
class AISituationModel:
    user_id: str
    situation: str | None
    name: str | None
    created_at: Any  # datetime
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    unlocked: bool

    @classmethod
    def from_row(cls, row: tuple) -> AISituationModel:
        return cls(*row)


@dataclass
class WarningModel:
    id: int
    guild_id: str
    user_id: str
    reason: str | None
    created_at: Any  # datetime
    expires_at: Any | None  # datetime
    created_by: str
    escalation_level: int

    @classmethod
    def from_row(cls, row: tuple) -> WarningModel:
        return cls(*row)


@dataclass
class DetailedWarningModel:
    # Subset projection from get_detailed_warnings()
    id: int
    reason: str | None
    created_at: Any  # datetime
    expires_at: Any | None  # datetime
    created_by: str

    @classmethod
    def from_row(cls, row: tuple) -> DetailedWarningModel:
        return cls(*row)


@dataclass
class WarnConfigModel:
    expiration_days: int
    timeout_threshold: int
    timeout_duration: int
    kick_threshold: int
    ban_threshold: int

    @classmethod
    def from_row(cls, row: tuple) -> WarnConfigModel:
        # row includes guild_id as first column, which we skip
        _, expiration_days, timeout_threshold, timeout_duration, kick_threshold, ban_threshold = row
        return cls(expiration_days, timeout_threshold, timeout_duration, kick_threshold, ban_threshold)


@dataclass
class XpBoostModel:
    boost: float
    additive: bool

    @classmethod
    def from_row(cls, row: tuple) -> XpBoostModel:
        return cls(*row)


@dataclass
class BlacklistEntryModel:
    entity_id: str
    reason: str | None = None

    @classmethod
    def from_row(cls, row: tuple) -> BlacklistEntryModel:
        return cls(*row)


@dataclass
class LevelRoleModel:
    level: int
    role_id: str

    @classmethod
    def from_row(cls, row: tuple) -> LevelRoleModel:
        return cls(*row)


@dataclass
class DynamicSlowmodeModel:
    guild_id: str
    channel_id: str
    messages: int
    per: int
    reset_after: int
    cached_slowmode: int | None

    @classmethod
    def from_row(cls, row: tuple) -> DynamicSlowmodeModel:
        return cls(*row)


@dataclass
class AfkMessageModel:
    message_id: str
    channel_id: str

    @classmethod
    def from_row(cls, row: tuple) -> AfkMessageModel:
        return cls(*row)


@dataclass
class LogBlacklistEntryModel:
    guild_id: str
    entity_id: str

    @classmethod
    def from_row(cls, row: tuple) -> LogBlacklistEntryModel:
        return cls(*row)


@dataclass
class WelcomeChannelModel:
    channel_id: str
    guild_id: str
    message: str | None
    image_background: str | None

    @classmethod
    def from_row(cls, row: tuple) -> WelcomeChannelModel:
        return cls(*row)


@dataclass
class LeaveChannelModel:
    channel_id: str
    guild_id: str
    message: str | None
    image_background: str | None

    @classmethod
    def from_row(cls, row: tuple) -> LeaveChannelModel:
        return cls(*row)


@dataclass
class DynamicSlowmodeMessageModel:
    id: int
    channel_id: str
    message_id: str
    send_time: Any  # datetime

    @classmethod
    def from_row(cls, row: tuple) -> DynamicSlowmodeMessageModel:
        return cls(*row)


@dataclass
class TokenOverviewModel:
    free_token: int
    plus_token: int
    paid_token: int
    used_token: int

    @classmethod
    def from_row(cls, row: tuple) -> TokenOverviewModel:
        return cls(*row)


@dataclass
class LogEnableModel:
    guild_id: str
    automod_rule_create: bool
    automod_rule_update: bool
    automod_rule_delete: bool
    automod_action: bool
    guild_channel_delete: bool
    guild_channel_create: bool
    guild_channel_update: bool
    guild_update: bool
    invite_create: bool
    invite_delete: bool
    member_join: bool
    member_leave: bool
    member_update: bool
    user_update: bool
    member_ban: bool
    member_unban: bool
    presence_update: bool
    message_edit: bool
    message_delete: bool
    reaction_add: bool
    reaction_remove: bool
    guild_role_create: bool
    guild_role_delete: bool
    guild_role_update: bool

    # Ordered list matching LOG_OPTIONS order (skipping guild_id)
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

    @classmethod
    def from_row(cls, row: tuple) -> LogEnableModel:
        guild_id = row[0]
        values = [bool(v) for v in row[1:25]]
        return cls(guild_id, *values)

    def get_option(self, index: int) -> bool:
        return getattr(self, self._OPTION_KEYS[index])

    def set_option(self, index: int, value: bool) -> None:
        setattr(self, self._OPTION_KEYS[index], value)


@dataclass
class ClaimedBoosterChannelModel:
    user_id: str
    channel_id: str
    guild_id: str

    @classmethod
    def from_row(cls, row: tuple) -> ClaimedBoosterChannelModel:
        return cls(*row)


@dataclass
class ClaimedBoosterRoleModel:
    user_id: str
    role_id: str
    guild_id: str

    @classmethod
    def from_row(cls, row: tuple) -> ClaimedBoosterRoleModel:
        return cls(*row)


@dataclass
class BlockedReporterModel:
    guild_id: str
    user_id: str

    @classmethod
    def from_row(cls, row: tuple) -> BlockedReporterModel:
        return cls(*row)


@dataclass
class LevelLeaderboardEntryModel:
    user_id: str
    xp: int

    @classmethod
    def from_row(cls, row: tuple) -> LevelLeaderboardEntryModel:
        return cls(*row)


@dataclass
class UserLevelInfoModel:
    xp: int
    level: int
    xp_needed: int
    custom_background: str | None


@dataclass
class ChannelOverwriteModel:
    role_id: str
    overwrites: dict

    @classmethod
    def from_row(cls, row: tuple) -> ChannelOverwriteModel:
        import json

        return cls(role_id=row[0], overwrites=json.loads(row[1]))


@dataclass
class LevelRolesGroupModel:
    level: int
    role_ids: list[str]

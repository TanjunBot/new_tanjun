"""Tests for all dataclass models in models.py — comprehensive."""

import json
from dataclasses import fields as dataclass_fields
from datetime import datetime

import pytest

from models import (
    AfkMessageModel,
    AISituationModel,
    BlacklistEntryModel,
    BlockedReporterModel,
    ChannelOverwriteModel,
    ClaimedBoosterChannelModel,
    ClaimedBoosterRoleModel,
    DetailedWarningModel,
    DynamicSlowmodeMessageModel,
    DynamicSlowmodeModel,
    GiveawayBlacklistEntryModel,
    GiveawayChannelRequirementModel,
    GiveawayModel,
    LeaveChannelModel,
    LevelLeaderboardEntryModel,
    LevelRoleModel,
    LevelRolesGroupModel,
    LogBlacklistEntryModel,
    LogEnableModel,
    ReportModel,
    ScheduledMessageModel,
    TicketMessageModel,
    TicketModel,
    TokenOverviewModel,
    TriggerMessageChannelModel,
    TriggerMessageModel,
    TwitchOnlineNotificationModel,
    UserLevelInfoModel,
    WarnConfigModel,
    WarningModel,
    WelcomeChannelModel,
    XpBoostModel,
)

# ==================== GiveawayModel ====================


class TestGiveawayModel:
    def test_from_row_all_fields(self) -> None:
        now = datetime.now()
        row = (
            1,
            "guild1",
            "Title",
            "Desc",
            3,
            True,
            "custom",
            "sponsor",
            "price",
            "msg",
            now,
            None,
            False,
            False,
            None,
            None,
            None,
            False,
            None,
            "pending",
            now,
        )
        model = GiveawayModel.from_row(row)
        assert model.giveaway_id == 1
        assert model.guild_id == "guild1"
        assert model.title == "Title"
        assert model.description == "Desc"
        assert model.winners == 3
        assert model.with_button is True
        assert model.custom_name == "custom"
        assert model.sponsor == "sponsor"
        assert model.price == "price"
        assert model.message == "msg"
        assert model.end_time == now
        assert model.start_time is None
        assert model.started is False
        assert model.ended is False
        assert model.new_message_requirement is None
        assert model.day_requirement is None
        assert model.voice_requirement is None
        assert model.send_failed is False
        assert model.channel_id is None
        assert model.message_id == "pending"
        assert model.created_at == now

    def test_from_row_with_none_fields(self) -> None:
        now = datetime.now()
        row = (
            2,
            "guild2",
            "Title2",
            None,
            1,
            False,
            None,
            None,
            None,
            None,
            now,
            None,
            False,
            False,
            None,
            None,
            None,
            False,
            None,
            "pending",
            now,
        )
        model = GiveawayModel.from_row(row)
        assert model.description is None
        assert model.custom_name is None
        assert model.with_button is False
        assert model.sponsor is None
        assert model.voice_requirement is None

    def test_from_row_wrong_field_count_raises(self) -> None:
        with pytest.raises(TypeError):
            GiveawayModel.from_row((1, "guild1"))

    def test_from_row_too_many_fields_raises(self) -> None:
        now = datetime.now()
        row = (
            1,
            "g",
            "t",
            "d",
            1,
            True,
            None,
            None,
            None,
            None,
            now,
            None,
            False,
            False,
            None,
            None,
            None,
            False,
            None,
            "m",
            now,
            "extra",
        )
        with pytest.raises(TypeError):
            GiveawayModel.from_row(row)

    def test_dataclass_fields_count(self) -> None:
        assert len(dataclass_fields(GiveawayModel)) == 21

    def test_from_row_preserves_types(self) -> None:
        """Dataclasses don't coerce types — int 1 stays int 1, not bool True."""
        now = datetime.now()
        row = (
            1,
            "guild1",
            "Title",
            "Desc",
            3,
            1,
            "custom",
            "sponsor",
            "price",
            "msg",
            now,
            None,
            1,
            0,
            None,
            None,
            None,
            1,
            None,
            "pending",
            now,
        )
        model = GiveawayModel.from_row(row)
        # Dataclass stores the exact types from the row — int stays int
        assert model.with_button == 1
        assert model.started == 1
        assert model.ended == 0

    def test_equality(self) -> None:
        now = datetime.now()
        row = (
            1,
            "g",
            "t",
            None,
            1,
            False,
            None,
            None,
            None,
            None,
            now,
            None,
            False,
            False,
            None,
            None,
            None,
            False,
            None,
            "m",
            now,
        )
        m1 = GiveawayModel.from_row(row)
        m2 = GiveawayModel.from_row(row)
        assert m1 == m2

    def test_inequality(self) -> None:
        now = datetime.now()
        row1 = (
            1,
            "g",
            "t",
            None,
            1,
            False,
            None,
            None,
            None,
            None,
            now,
            None,
            False,
            False,
            None,
            None,
            None,
            False,
            None,
            "m",
            now,
        )
        row2 = (
            2,
            "g",
            "t",
            None,
            1,
            False,
            None,
            None,
            None,
            None,
            now,
            None,
            False,
            False,
            None,
            None,
            None,
            False,
            None,
            "m",
            now,
        )
        m1 = GiveawayModel.from_row(row1)
        m2 = GiveawayModel.from_row(row2)
        assert m1 != m2


# ==================== GiveawayChannelRequirementModel ====================


class TestGiveawayChannelRequirementModel:
    def test_from_row(self) -> None:
        model = GiveawayChannelRequirementModel.from_row(("12345", 5))
        assert model.channel_id == "12345"
        assert model.amount == 5

    def test_from_row_zero_amount(self) -> None:
        model = GiveawayChannelRequirementModel.from_row(("99999", 0))
        assert model.amount == 0

    def test_from_row_negative_amount(self) -> None:
        model = GiveawayChannelRequirementModel.from_row(("99999", -1))
        assert model.amount == -1

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            GiveawayChannelRequirementModel.from_row(("12345",))


# ==================== GiveawayBlacklistEntryModel ====================


class TestGiveawayBlacklistEntryModel:
    def test_from_row_with_reason(self) -> None:
        model = GiveawayBlacklistEntryModel.from_row(("99999", "spam"))
        assert model.entity_id == "99999"
        assert model.reason == "spam"

    def test_from_row_without_reason(self) -> None:
        model = GiveawayBlacklistEntryModel.from_row(("99999", None))
        assert model.reason is None

    def test_default_reason_is_none(self) -> None:
        model = GiveawayBlacklistEntryModel(entity_id="123")
        assert model.reason is None

    def test_from_row_single_element_uses_default(self) -> None:
        """reason has a default, so a 1-element tuple should work."""
        model = GiveawayBlacklistEntryModel.from_row(("99999",))
        assert model.entity_id == "99999"
        assert model.reason is None

    def test_from_row_too_many_raises(self) -> None:
        with pytest.raises(TypeError):
            GiveawayBlacklistEntryModel.from_row(("a", "b", "c"))


# ==================== ReportModel ====================


class TestReportModel:
    def test_from_row_all_fields(self) -> None:
        model = ReportModel.from_row((1, "g1", "u1", "r1", "bad", 1700000000, True, 1700001000, "admin1", False, None, None))
        assert model.id == 1
        assert model.guild_id == "g1"
        assert model.user_id == "u1"
        assert model.reporter_id == "r1"
        assert model.reason == "bad"
        assert model.created_at == 1700000000
        assert model.accepted is True
        assert model.accepted_at == 1700001000
        assert model.accepted_by == "admin1"
        assert model.resolved is False
        assert model.resolved_at is None
        assert model.resolved_by is None

    def test_from_row_none_reason(self) -> None:
        model = ReportModel.from_row((2, "g1", "u1", "r1", None, 1700000000, False, None, None, True, 1700002000, "admin2"))
        assert model.reason is None
        assert model.accepted is False
        assert model.resolved is True

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            ReportModel.from_row((1, "g1"))

    def test_timestamps_are_int(self) -> None:
        model = ReportModel.from_row((1, "g1", "u1", "r1", None, 1700000000, False, None, None, False, None, None))
        assert isinstance(model.created_at, int)


# ==================== ScheduledMessageModel ====================


class TestScheduledMessageModel:
    def test_from_row_with_repeat(self) -> None:
        now = datetime.now()
        model = ScheduledMessageModel.from_row((1, "g1", "c1", "u1", "hello", now, 60, 3, None, now))
        assert model.repeat_interval == 60
        assert model.repeat_amount == 3

    def test_from_row_no_repeat(self) -> None:
        now = datetime.now()
        model = ScheduledMessageModel.from_row((2, "g1", "c1", "u1", "hello", now, None, None, None, now))
        assert model.repeat_interval is None
        assert model.repeat_amount is None

    def test_from_row_none_guild_and_channel(self) -> None:
        now = datetime.now()
        model = ScheduledMessageModel.from_row((3, None, None, "u1", "dm", now, None, None, None, now))
        assert model.guild_id is None
        assert model.channel_id is None


# ==================== TriggerMessageModel ====================


class TestTriggerMessageModel:
    def test_from_row_case_sensitive_true(self) -> None:
        model = TriggerMessageModel.from_row((1, "g1", "hello", "world", True))
        assert model.case_sensitive is True

    def test_from_row_case_sensitive_false(self) -> None:
        model = TriggerMessageModel.from_row((2, "g1", "hello", "world", False))
        assert model.case_sensitive is False

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            TriggerMessageModel.from_row((1, "g1", "hello"))


# ==================== TicketMessageModel ====================


class TestTicketMessageModel:
    def test_from_row_all_fields(self) -> None:
        model = TicketMessageModel.from_row((1, "g1", "c1", "Welcome!", "123", "Help", "Desc", "456"))
        assert model.introduction == "Welcome!"
        assert model.ping_role == "123"
        assert model.name == "Help"
        assert model.summary_channel_id == "456"

    def test_from_row_none_optional_fields(self) -> None:
        model = TicketMessageModel.from_row((2, "g1", "c1", None, None, None, "Desc", None))
        assert model.introduction is None
        assert model.ping_role is None
        assert model.name is None
        assert model.summary_channel_id is None


# ==================== TicketModel ====================


class TestTicketModel:
    def test_from_row_open_ticket(self) -> None:
        model = TicketModel.from_row(("g1", "u1", 1700000000, False, None, None, "c1", 1))
        assert model.opened_at == 1700000000
        assert model.closed is False
        assert model.closed_at is None
        assert model.closed_by is None

    def test_from_row_closed_ticket(self) -> None:
        model = TicketModel.from_row(("g1", "u1", 1700000000, True, 1700001000, "admin1", "c1", 1))
        assert model.closed is True
        assert model.closed_at == 1700001000
        assert model.closed_by == "admin1"


# ==================== AISituationModel ====================


class TestAISituationModel:
    def test_from_row_with_all_fields(self) -> None:
        now = datetime.now()
        model = AISituationModel.from_row(("u1", "pirate", "Captain", now, 0.7, 0.9, 0.5, 0.2, True))
        assert model.temperature == 0.7
        assert model.top_p == 0.9
        assert model.frequency_penalty == 0.5
        assert model.presence_penalty == 0.2
        assert model.unlocked is True

    def test_from_row_with_nulls(self) -> None:
        now = datetime.now()
        model = AISituationModel.from_row(("u1", None, None, now, 1.0, 1.0, 0.0, 0.0, False))
        assert model.situation is None
        assert model.name is None
        assert model.unlocked is False

    def test_from_row_extreme_float_values(self) -> None:
        """No validation on float ranges — negative/out-of-range accepted."""
        now = datetime.now()
        model = AISituationModel.from_row(("u1", "s", "n", now, -1.0, 2.0, 3.0, -0.5, True))
        assert model.temperature == -1.0
        assert model.top_p == 2.0

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            AISituationModel.from_row(("u1", "s", "n"))


# ==================== WarningModel / DetailedWarningModel ====================


class TestWarningModel:
    def test_from_row_with_expiration(self) -> None:
        now = datetime.now()
        future = datetime(2030, 1, 1)
        model = WarningModel.from_row((1, "g1", "u1", "spam", now, future, "admin1", 2))
        assert model.expires_at == future
        assert model.escalation_level == 2

    def test_from_row_without_expiration(self) -> None:
        now = datetime.now()
        model = WarningModel.from_row((2, "g1", "u1", "spam", now, None, "admin1", 0))
        assert model.expires_at is None
        assert model.escalation_level == 0

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            WarningModel.from_row((1, "g1", "u1"))


class TestDetailedWarningModel:
    def test_from_row(self) -> None:
        now = datetime.now()
        model = DetailedWarningModel.from_row((1, "spam", now, None, "admin1"))
        assert model.id == 1
        assert model.reason == "spam"
        assert model.created_at == now
        assert model.expires_at is None
        assert model.created_by == "admin1"

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            DetailedWarningModel.from_row((1, "spam"))


# ==================== WarnConfigModel ====================


class TestWarnConfigModel:
    def test_from_row(self) -> None:
        row = ("guild1", 7, 3, 60, 5, 10)
        model = WarnConfigModel.from_row(row)
        assert model.expiration_days == 7
        assert model.timeout_threshold == 3
        assert model.timeout_duration == 60
        assert model.kick_threshold == 5
        assert model.ban_threshold == 10

    def test_from_row_skips_guild_id(self) -> None:
        row = ("guild1", 14, 5, 120, 10, 20)
        model = WarnConfigModel.from_row(row)
        assert model.expiration_days == 14
        assert model.ban_threshold == 20

    def test_from_row_zero_values(self) -> None:
        row = ("guild2", 0, 0, 0, 0, 0)
        model = WarnConfigModel.from_row(row)
        assert model.expiration_days == 0
        assert model.timeout_threshold == 0

    def test_from_row_too_short_raises(self) -> None:
        with pytest.raises(ValueError):
            WarnConfigModel.from_row(("guild1", 7, 3))

    def test_from_row_too_long_raises(self) -> None:
        """Extra elements should raise ValueError since destructuring is strict."""
        with pytest.raises(ValueError):
            WarnConfigModel.from_row(("guild1", 7, 3, 60, 5, 10, "extra"))

    def test_from_row_exactly_six(self) -> None:
        row = ("guild1", 14, 5, 120, 10, 20)
        model = WarnConfigModel.from_row(row)
        assert model.expiration_days == 14

    def test_from_row_negative_values(self) -> None:
        """No validation — negative values accepted."""
        row = ("guild1", -1, -1, -1, -1, -1)
        model = WarnConfigModel.from_row(row)
        assert model.expiration_days == -1


# ==================== XpBoostModel ====================


class TestXpBoostModel:
    def test_from_row_multiplicative(self) -> None:
        model = XpBoostModel.from_row((1.5, False))
        assert model.boost == 1.5
        assert model.additive is False

    def test_from_row_additive(self) -> None:
        model = XpBoostModel.from_row((0.5, True))
        assert model.boost == 0.5
        assert model.additive is True

    def test_from_row_boost_of_one(self) -> None:
        model = XpBoostModel.from_row((1.0, False))
        assert model.boost == 1.0

    def test_from_row_zero_boost(self) -> None:
        model = XpBoostModel.from_row((0.0, True))
        assert model.boost == 0.0
        assert model.additive is True

    def test_from_row_negative_boost(self) -> None:
        """No validation — negative boost values accepted."""
        model = XpBoostModel.from_row((-0.5, False))
        assert model.boost == -0.5


# ==================== BlacklistEntryModel ====================


class TestBlacklistEntryModel:
    def test_from_row_with_reason(self) -> None:
        model = BlacklistEntryModel.from_row(("12345", "spam"))
        assert model.entity_id == "12345"
        assert model.reason == "spam"

    def test_from_row_without_reason(self) -> None:
        model = BlacklistEntryModel.from_row(("12345", None))
        assert model.reason is None

    def test_default_reason_is_none(self) -> None:
        model = BlacklistEntryModel(entity_id="123")
        assert model.reason is None

    def test_from_row_single_element(self) -> None:
        """reason has a default, so a 1-element tuple should work."""
        model = BlacklistEntryModel.from_row(("12345",))
        assert model.entity_id == "12345"
        assert model.reason is None

    def test_from_row_too_many_raises(self) -> None:
        with pytest.raises(TypeError):
            BlacklistEntryModel.from_row(("a", "b", "c"))


# ==================== LogEnableModel ====================


class TestLogEnableModel:
    def test_from_row(self) -> None:
        row = (
            "guild1",
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
        )
        model = LogEnableModel.from_row(row)
        assert model.guild_id == "guild1"
        assert model.automod_rule_create is True
        assert model.automod_rule_update is False
        assert model.automod_rule_delete is True
        assert model.guild_role_create is True
        assert model.guild_role_delete is False

    def test_from_row_all_true(self) -> None:
        row = ("guild1",) + tuple([True] * 24)
        model = LogEnableModel.from_row(row)
        assert model.guild_id == "guild1"
        for key in LogEnableModel._OPTION_KEYS:
            assert getattr(model, key) is True

    def test_from_row_all_false(self) -> None:
        row = ("guild1",) + tuple([False] * 24)
        model = LogEnableModel.from_row(row)
        for key in LogEnableModel._OPTION_KEYS:
            assert getattr(model, key) is False

    def test_from_row_integer_values_cast_to_bool(self) -> None:
        """from_row casts row[1:25] through bool(), so 1 -> True, 0 -> False."""
        row = ("guild1",) + tuple([1, 0] * 12)
        model = LogEnableModel.from_row(row)
        assert model.automod_rule_create is True
        assert model.automod_rule_update is False

    def test_from_row_nonzero_integers_are_truthy(self) -> None:
        """bool(2) is True, bool(-1) is True."""
        row = ("guild1",) + tuple([2, -1] * 12)
        model = LogEnableModel.from_row(row)
        assert model.automod_rule_create is True
        assert model.automod_rule_update is True

    def test_from_row_empty_string_is_falsy(self) -> None:
        """bool('') is False, bool('0') is True (non-empty string)."""
        row = ("guild1",) + tuple(["", "0"] * 12)
        model = LogEnableModel.from_row(row)
        assert model.automod_rule_create is False
        assert model.automod_rule_update is True

    def test_get_option_valid_indices(self) -> None:
        row = ("guild1",) + tuple([True] * 24)
        model = LogEnableModel.from_row(row)
        assert model.get_option(0) is True
        assert model.get_option(23) is True

    def test_get_option_invalid_index_raises(self) -> None:
        row = ("guild1",) + tuple([True] * 24)
        model = LogEnableModel.from_row(row)
        with pytest.raises(IndexError):
            model.get_option(24)

    def test_get_option_negative_index_wraps(self) -> None:
        """Python negative indexing wraps around — this is expected behavior."""
        row = ("guild1",) + tuple([True] * 24)
        model = LogEnableModel.from_row(row)
        # -1 should return the last option (guild_role_update)
        result = model.get_option(-1)
        assert result is True  # all True in this test

    def test_set_option_valid(self) -> None:
        row = ("guild1",) + tuple([True] * 24)
        model = LogEnableModel.from_row(row)
        model.set_option(0, False)
        assert model.get_option(0) is False
        assert model.automod_rule_create is False

    def test_set_option_invalid_index_raises(self) -> None:
        row = ("guild1",) + tuple([True] * 24)
        model = LogEnableModel.from_row(row)
        with pytest.raises(IndexError):
            model.set_option(24, False)

    def test_set_option_stores_non_bool(self) -> None:
        """Dataclass fields have no type enforcement — any value can be stored."""
        row = ("guild1",) + tuple([True] * 24)
        model = LogEnableModel.from_row(row)
        model.set_option(0, "not_a_bool")  # type: ignore[arg-type]
        assert model.automod_rule_create == "not_a_bool"

    def test_option_keys_match_field_names(self) -> None:
        row = ("guild1",) + tuple([False] * 24)
        model = LogEnableModel.from_row(row)
        for key in LogEnableModel._OPTION_KEYS:
            assert hasattr(model, key), f"Missing attribute: {key}"

    def test_option_keys_count(self) -> None:
        assert len(LogEnableModel._OPTION_KEYS) == 24

    def test_from_row_too_short_raises(self) -> None:
        """Row with fewer than 25 elements should fail."""
        with pytest.raises((TypeError, IndexError)):
            LogEnableModel.from_row(("guild1", True))

    def test_from_row_too_long_still_works(self) -> None:
        """Extra elements beyond index 24 are silently ignored by row[0]/row[1:25]."""
        row = ("guild1",) + tuple([True] * 24) + ("extra",)
        model = LogEnableModel.from_row(row)
        assert model.automod_rule_create is True


# ==================== ChannelOverwriteModel ====================


class TestChannelOverwriteModel:
    def test_from_row_parses_json(self) -> None:
        overwrites_dict = {"send_messages": False, "read_messages": True}
        row = ("role1", json.dumps(overwrites_dict))
        model = ChannelOverwriteModel.from_row(row)
        assert model.role_id == "role1"
        assert model.overwrites == overwrites_dict

    def test_from_row_complex_json(self) -> None:
        overwrites_dict = {"send_messages": False, "embed_links": True, "attach_files": True}
        row = ("role2", json.dumps(overwrites_dict))
        model = ChannelOverwriteModel.from_row(row)
        assert len(model.overwrites) == 3

    def test_from_row_empty_json(self) -> None:
        row = ("role3", "{}")
        model = ChannelOverwriteModel.from_row(row)
        assert model.overwrites == {}

    def test_from_row_invalid_json_raises(self) -> None:
        with pytest.raises(json.JSONDecodeError):
            ChannelOverwriteModel.from_row(("role4", "not json{"))

    def test_from_row_none_json_raises(self) -> None:
        """json.loads(None) raises TypeError."""
        with pytest.raises(TypeError):
            ChannelOverwriteModel.from_row(("role4", None))

    def test_from_row_dict_as_overwrites_raises(self) -> None:
        """json.loads expects str/bytes, not dict."""
        with pytest.raises(TypeError):
            ChannelOverwriteModel.from_row(("role4", {"key": "val"}))

    def test_from_row_nested_json(self) -> None:
        overwrites_dict = {"permissions": {"admin": True, "mod": False}}
        row = ("role5", json.dumps(overwrites_dict))
        model = ChannelOverwriteModel.from_row(row)
        assert model.overwrites["permissions"]["admin"] is True

    def test_from_row_numeric_values(self) -> None:
        overwrites_dict = {"bitmask": 12345}
        row = ("role6", json.dumps(overwrites_dict))
        model = ChannelOverwriteModel.from_row(row)
        assert model.overwrites["bitmask"] == 12345

    def test_from_row_list_json(self) -> None:
        """json.loads can return a list — overwrites would be a list, not dict."""
        row = ("role7", "[1, 2, 3]")
        model = ChannelOverwriteModel.from_row(row)
        assert isinstance(model.overwrites, list)
        assert model.overwrites == [1, 2, 3]


# ==================== DynamicSlowmodeModel ====================


class TestDynamicSlowmodeModel:
    def test_from_row_without_cached_slowmode(self) -> None:
        model = DynamicSlowmodeModel.from_row(("g1", "c1", 5, 10, 30, None))
        assert model.cached_slowmode is None

    def test_from_row_with_cached_slowmode(self) -> None:
        model = DynamicSlowmodeModel.from_row(("g1", "c1", 5, 10, 30, 15))
        assert model.cached_slowmode == 15

    def test_from_row_zero_values(self) -> None:
        model = DynamicSlowmodeModel.from_row(("g1", "c1", 0, 0, 0, 0))
        assert model.messages == 0
        assert model.per == 0
        assert model.reset_after == 0
        assert model.cached_slowmode == 0


# ==================== WelcomeChannelModel / LeaveChannelModel ====================


class TestWelcomeChannelModel:
    def test_from_row_all_fields(self) -> None:
        model = WelcomeChannelModel.from_row(("c1", "g1", "Welcome!", "bg.png"))
        assert model.channel_id == "c1"
        assert model.guild_id == "g1"
        assert model.message == "Welcome!"
        assert model.image_background == "bg.png"

    def test_from_row_null_optional_fields(self) -> None:
        model = WelcomeChannelModel.from_row(("c1", "g1", None, None))
        assert model.message is None
        assert model.image_background is None

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            WelcomeChannelModel.from_row(("c1",))

    def test_equality(self) -> None:
        row = ("c1", "g1", "Welcome!", "bg.png")
        m1 = WelcomeChannelModel.from_row(row)
        m2 = WelcomeChannelModel.from_row(row)
        assert m1 == m2


class TestLeaveChannelModel:
    def test_from_row_all_fields(self) -> None:
        model = LeaveChannelModel.from_row(("c1", "g1", "Goodbye!", "bg.png"))
        assert model.channel_id == "c1"
        assert model.message == "Goodbye!"

    def test_from_row_null_optional_fields(self) -> None:
        model = LeaveChannelModel.from_row(("c1", "g1", None, None))
        assert model.message is None
        assert model.image_background is None

    def test_leave_channel_same_structure_as_welcome(self) -> None:
        """WelcomeChannelModel and LeaveChannelModel have the same fields but are different classes."""
        row = ("c1", "g1", "msg", None)
        welcome = WelcomeChannelModel.from_row(row)
        leave = LeaveChannelModel.from_row(row)
        assert type(welcome) != type(leave)


# ==================== TokenOverviewModel ====================


class TestTokenOverviewModel:
    def test_from_row(self) -> None:
        model = TokenOverviewModel.from_row((100, 50, 25, 75))
        assert model.free_token == 100
        assert model.plus_token == 50
        assert model.paid_token == 25
        assert model.used_token == 75

    def test_from_row_zero_values(self) -> None:
        model = TokenOverviewModel.from_row((0, 0, 0, 0))
        assert model.free_token == 0
        assert model.plus_token == 0

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            TokenOverviewModel.from_row((100, 50))


# ==================== LogBlacklistEntryModel ====================


class TestLogBlacklistEntryModel:
    def test_from_row(self) -> None:
        model = LogBlacklistEntryModel.from_row(("guild1", "entity1"))
        assert model.guild_id == "guild1"
        assert model.entity_id == "entity1"

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            LogBlacklistEntryModel.from_row(("guild1",))


# ==================== AfkMessageModel ====================


class TestAfkMessageModel:
    def test_from_row(self) -> None:
        model = AfkMessageModel.from_row(("msg1", "chan1"))
        assert model.message_id == "msg1"
        assert model.channel_id == "chan1"

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            AfkMessageModel.from_row(("msg1",))


# ==================== DynamicSlowmodeMessageModel ====================


class TestDynamicSlowmodeMessageModel:
    def test_from_row(self) -> None:
        now = datetime.now()
        model = DynamicSlowmodeMessageModel.from_row((1, "chan1", "msg1", now))
        assert model.id == 1
        assert model.channel_id == "chan1"
        assert model.message_id == "msg1"
        assert model.send_time == now

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            DynamicSlowmodeMessageModel.from_row((1,))


# ==================== LevelRoleModel / LevelRolesGroupModel ====================


class TestLevelRoleModel:
    def test_from_row(self) -> None:
        model = LevelRoleModel.from_row((10, "role123"))
        assert model.level == 10
        assert model.role_id == "role123"

    def test_from_row_level_zero(self) -> None:
        model = LevelRoleModel.from_row((0, "role0"))
        assert model.level == 0

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            LevelRoleModel.from_row((10,))


class TestLevelRolesGroupModel:
    def test_fields(self) -> None:
        group = LevelRolesGroupModel(level=10, role_ids=["r1", "r2"])
        assert group.level == 10
        assert group.role_ids == ["r1", "r2"]

    def test_empty_role_ids(self) -> None:
        group = LevelRolesGroupModel(level=1, role_ids=[])
        assert group.role_ids == []

    def test_multiple_roles(self) -> None:
        group = LevelRolesGroupModel(level=50, role_ids=["r1", "r2", "r3"])
        assert len(group.role_ids) == 3

    def test_no_from_row(self) -> None:
        assert not hasattr(LevelRolesGroupModel, "from_row")


# ==================== ClaimedBoosterChannelModel / ClaimedBoosterRoleModel ====================


class TestClaimedBoosterChannelModel:
    def test_from_row(self) -> None:
        model = ClaimedBoosterChannelModel.from_row(("u1", "c1", "g1"))
        assert model.user_id == "u1"
        assert model.channel_id == "c1"
        assert model.guild_id == "g1"

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            ClaimedBoosterChannelModel.from_row(("u1", "c1"))


class TestClaimedBoosterRoleModel:
    def test_from_row(self) -> None:
        model = ClaimedBoosterRoleModel.from_row(("u1", "r1", "g1"))
        assert model.user_id == "u1"
        assert model.role_id == "r1"
        assert model.guild_id == "g1"

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            ClaimedBoosterRoleModel.from_row(("u1", "r1"))


# ==================== BlockedReporterModel ====================


class TestBlockedReporterModel:
    def test_from_row(self) -> None:
        model = BlockedReporterModel.from_row(("guild1", "user1"))
        assert model.guild_id == "guild1"
        assert model.user_id == "user1"

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            BlockedReporterModel.from_row(("guild1",))


# ==================== LevelLeaderboardEntryModel ====================


class TestLevelLeaderboardEntryModel:
    def test_from_row(self) -> None:
        model = LevelLeaderboardEntryModel.from_row(("user1", 5000))
        assert model.user_id == "user1"
        assert model.xp == 5000

    def test_from_row_zero_xp(self) -> None:
        model = LevelLeaderboardEntryModel.from_row(("user2", 0))
        assert model.xp == 0

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            LevelLeaderboardEntryModel.from_row(("user1",))


# ==================== UserLevelInfoModel ====================


class TestUserLevelInfoModel:
    def test_fields(self) -> None:
        info = UserLevelInfoModel(xp=1000, level=5, xp_needed=500, custom_background="bg.png")
        assert info.xp == 1000
        assert info.level == 5
        assert info.xp_needed == 500
        assert info.custom_background == "bg.png"

    def test_fields_none_background(self) -> None:
        info = UserLevelInfoModel(xp=0, level=1, xp_needed=100, custom_background=None)
        assert info.custom_background is None

    def test_no_from_row(self) -> None:
        assert not hasattr(UserLevelInfoModel, "from_row")


# ==================== TwitchOnlineNotificationModel ====================


class TestTwitchOnlineNotificationModel:
    def test_from_row_with_message(self) -> None:
        model = TwitchOnlineNotificationModel.from_row((1, "c1", "g1", "uuid1", "streamer", "going live!"))
        assert model.notification_message == "going live!"
        assert model.twitch_name == "streamer"

    def test_from_row_without_message(self) -> None:
        model = TwitchOnlineNotificationModel.from_row((2, "c2", "g2", "uuid2", "streamer2", None))
        assert model.notification_message is None

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            TwitchOnlineNotificationModel.from_row((1, "c1", "g1"))


# ==================== TriggerMessageChannelModel ====================


class TestTriggerMessageChannelModel:
    def test_from_row(self) -> None:
        model = TriggerMessageChannelModel.from_row(("g1", "c1", 42))
        assert model.guild_id == "g1"
        assert model.channel_id == "c1"
        assert model.trigger_id == 42

    def test_from_row_wrong_length_raises(self) -> None:
        with pytest.raises(TypeError):
            TriggerMessageChannelModel.from_row(("g1", "c1"))

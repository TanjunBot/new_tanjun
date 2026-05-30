"""Tests for models.py from_row methods and model validation."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from models import (
    AfkMessageModel,
    AISituationModel,
    BlacklistEntryModel,
    BlockedReporterModel,
    ChannelOverwriteModel,
    ClaimedBoosterChannelModel,
    ClaimedBoosterRoleModel,
    CountingConfigModel,
    CountingModesConfigModel,
    DetailedWarningModel,
    DynamicSlowmodeMessageModel,
    DynamicSlowmodeModel,
    GiveawayBlacklistEntryModel,
    GiveawayChannelRequirementModel,
    GiveawayModel,
    LeaveChannelModel,
    LevelConfig,
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
    TwitchUserModel,
    UserLevelInfoModel,
    WarnConfigModel,
    WarningModel,
    WelcomeChannelModel,
    XpBoostModel,
)
from tests.helpers.factories import (
    CHANNEL_ID,
    GUILD_ID,
    MESSAGE_ID,
    ROLE_ID,
    USER_ID,
    _dt,
    afk_row,
    giveaway_row,
    level_role_row,
    warning_row,
    xp_boost_row,
)


def _snowflake(n: int = 1) -> str:
    return str(12345678901234560 + n)


class TestXpBoostModel:
    def test_from_row(self):
        model = XpBoostModel.from_row(xp_boost_row(2.5, True))
        assert model.boost == 2.5
        assert model.additive is True

    def test_from_row_wrong_length_raises(self):
        with pytest.raises(ValueError, match="expected 2 columns"):
            XpBoostModel.from_row((1.0,))


class TestGiveawayModel:
    def test_from_row(self):
        model = GiveawayModel.from_row(giveaway_row())
        assert model.giveaway_id == 1
        assert model.guild_id == GUILD_ID
        assert model.title == "Test Giveaway"
        assert model.winners == 1
        assert model.started is True
        assert model.ended is False

    def test_from_row_custom_values(self):
        row = list(giveaway_row())
        row[1] = "99988877766666666"
        row[2] = "Custom Title"
        model = GiveawayModel.from_row(tuple(row))
        assert model.guild_id == "99988877766666666"
        assert model.title == "Custom Title"


class TestGiveawayChannelRequirementModel:
    def test_from_row(self):
        model = GiveawayChannelRequirementModel.from_row((CHANNEL_ID, 5))
        assert model.channel_id == CHANNEL_ID
        assert model.amount == 5


class TestGiveawayBlacklistEntryModel:
    def test_from_row(self):
        model = GiveawayBlacklistEntryModel.from_row((USER_ID, "spam"))
        assert model.entity_id == USER_ID
        assert model.reason == "spam"


class TestReportModel:
    def test_from_row(self):
        model = ReportModel.from_row(
            (1, GUILD_ID, USER_ID, "22222222222222222", "reason", 1700000000, "pending", 1700000100, "33333333333333333", None, False)
        )
        assert model.id == 1
        assert model.status == "pending"
        assert model.anonymous is False


class TestScheduledMessageModel:
    def test_from_row(self):
        dt = _dt()
        model = ScheduledMessageModel.from_row(
            (1, GUILD_ID, CHANNEL_ID, USER_ID, "hello", dt, 3600, 5, None, None, dt)
        )
        assert model.message_id == 1
        assert model.content == "hello"
        assert model.repeat_interval == 3600


class TestTwitchOnlineNotificationModel:
    def test_from_row(self):
        model = TwitchOnlineNotificationModel.from_row(
            (1, CHANNEL_ID, GUILD_ID, "uuid-123", "streamer", "Live now!")
        )
        assert model.twitch_uuid == "uuid-123"
        assert model.notification_message == "Live now!"


class TestTriggerMessageModel:
    def test_from_row(self):
        model = TriggerMessageModel.from_row((1, GUILD_ID, "hello", "world", False))
        assert model.trigger == "hello"
        assert model.case_sensitive is False


class TestTriggerMessageChannelModel:
    def test_from_row(self):
        model = TriggerMessageChannelModel.from_row((GUILD_ID, CHANNEL_ID, 1))
        assert model.trigger_id == 1


class TestTicketMessageModel:
    def test_from_row(self):
        model = TicketMessageModel.from_row(
            (1, GUILD_ID, CHANNEL_ID, "intro", ROLE_ID, "Support", "desc", "55555555555555555")
        )
        assert model.name == "Support"


class TestTicketModel:
    def test_from_row(self):
        model = TicketModel.from_row(
            (GUILD_ID, USER_ID, 1700000000, False, None, None, CHANNEL_ID, 1)
        )
        assert model.closed is False
        assert model.ticket_message_id == 1


class TestAISituationModel:
    def test_from_row(self):
        dt = _dt()
        model = AISituationModel.from_row(
            (USER_ID, "situation text", "name", dt, 0.7, 1.0, 0.0, 0.0, True)
        )
        assert model.temperature == 0.7
        assert model.unlocked is True


class TestWarningModel:
    def test_from_row(self):
        model = WarningModel.from_row(warning_row())
        assert model.guild_id == GUILD_ID
        assert model.reason == "Test reason"

    def test_from_row_with_expiry(self):
        dt = _dt()
        row = (1, GUILD_ID, USER_ID, "reason", dt, dt, "22222222222222222", 2)
        model = WarningModel.from_row(row)
        assert model.escalation_level == 2


class TestDetailedWarningModel:
    def test_from_row(self):
        dt = _dt()
        model = DetailedWarningModel.from_row((1, "reason", dt, None, "22222222222222222"))
        assert model.created_by == "22222222222222222"


class TestWarnConfigModel:
    def test_from_row_skips_guild_id(self):
        model = WarnConfigModel.from_row(
            (GUILD_ID, 30, 3, 600, 5, 10)
        )
        assert model.expiration_days == 30
        assert model.ban_threshold == 10


class TestBlacklistEntryModel:
    def test_from_row(self):
        model = BlacklistEntryModel.from_row((USER_ID, None))
        assert model.entity_id == USER_ID
        assert model.reason is None


class TestLevelRoleModel:
    def test_from_row(self):
        model = LevelRoleModel.from_row(level_role_row(10, "88888888888888888"))
        assert model.level == 10
        assert model.role_id == "88888888888888888"


class TestDynamicSlowmodeModel:
    def test_from_row(self):
        model = DynamicSlowmodeModel.from_row((GUILD_ID, CHANNEL_ID, 5, 10, 60, 30))
        assert model.messages == 5
        assert model.cached_slowmode == 30


class TestAfkMessageModel:
    def test_from_row(self):
        model = AfkMessageModel.from_row((MESSAGE_ID, CHANNEL_ID))
        assert model.message_id == MESSAGE_ID


class TestLogBlacklistEntryModel:
    def test_from_row(self):
        model = LogBlacklistEntryModel.from_row((GUILD_ID, CHANNEL_ID))
        assert model.entity_id == CHANNEL_ID


class TestWelcomeChannelModel:
    def test_from_row(self):
        model = WelcomeChannelModel.from_row((CHANNEL_ID, GUILD_ID, "Welcome!", None))
        assert model.message == "Welcome!"


class TestLeaveChannelModel:
    def test_from_row(self):
        model = LeaveChannelModel.from_row((CHANNEL_ID, GUILD_ID, "Goodbye!", "bg.png"))
        assert model.image_background == "bg.png"


class TestDynamicSlowmodeMessageModel:
    def test_from_row(self):
        dt = _dt()
        model = DynamicSlowmodeMessageModel.from_row((1, CHANNEL_ID, MESSAGE_ID, dt))
        assert model.message_id == MESSAGE_ID


class TestTokenOverviewModel:
    def test_from_row(self):
        model = TokenOverviewModel.from_row((100, 50, 25, 10))
        assert model.free_token == 100
        assert model.used_token == 10


class TestLogEnableModel:
    def test_from_row(self):
        flags = [True] * 24
        row = (GUILD_ID, *flags)
        model = LogEnableModel.from_row(row)
        assert model.guild_id == GUILD_ID
        assert model.member_join is True
        assert model.automod_action is True

    def test_from_row_wrong_length_raises(self):
        with pytest.raises(ValueError, match="expected 25 columns"):
            LogEnableModel.from_row((GUILD_ID, True))

    def test_options_property(self):
        flags = [False] * 24
        model = LogEnableModel.from_row((GUILD_ID, *flags))
        opts = model.options
        assert "guild_id" not in opts
        assert all(v is False for v in opts.values())

    def test_get_set_option(self):
        flags = [True] * 24
        model = LogEnableModel.from_row((GUILD_ID, *flags))
        assert model.get_option(0) is True
        model.set_option(0, False)
        assert model.get_option(0) is False

    def test_coerce_ints_to_bools(self):
        model = LogEnableModel(guild_id=GUILD_ID, member_join=1, member_leave=0)
        assert model.member_join is True
        assert model.member_leave is False


class TestClaimedBoosterModels:
    def test_channel_from_row(self):
        model = ClaimedBoosterChannelModel.from_row((USER_ID, CHANNEL_ID, GUILD_ID))
        assert model.channel_id == CHANNEL_ID

    def test_role_from_row(self):
        model = ClaimedBoosterRoleModel.from_row((USER_ID, ROLE_ID, GUILD_ID))
        assert model.role_id == ROLE_ID


class TestBlockedReporterModel:
    def test_from_row(self):
        model = BlockedReporterModel.from_row((GUILD_ID, USER_ID))
        assert model.user_id == USER_ID


class TestLevelLeaderboardEntryModel:
    def test_from_row(self):
        model = LevelLeaderboardEntryModel.from_row((USER_ID, 5000))
        assert model.xp == 5000


class TestChannelOverwriteModel:
    def test_from_row_parses_json(self):
        model = ChannelOverwriteModel.from_row((ROLE_ID, '{"view_channel": true}'))
        assert model.role_id == ROLE_ID
        assert model.overwrites == {"view_channel": True}


class TestLevelConfig:
    def test_from_row(self):
        model = LevelConfig.from_row(
            (GUILD_ID, 1, "medium", None, 1, "Level up!", CHANNEL_ID, 60, 120)
        )
        assert model.active is True
        assert model.difficulty == "medium"
        assert model.text_cooldown == 60
        assert model.voice_cooldown == 120

    def test_from_row_wrong_length_raises(self):
        with pytest.raises(ValueError, match="expects exactly 9 columns"):
            LevelConfig.from_row((GUILD_ID, True))


class TestCountingModels:
    def test_counting_config_from_row(self):
        model = CountingConfigModel.from_row((42, _snowflake(), GUILD_ID))
        assert model.progress == 42

    def test_counting_modes_config_from_row(self):
        model = CountingModesConfigModel.from_row((10, 3, 100, _snowflake(2), GUILD_ID))
        assert model.mode == 3
        assert model.goal == 100


class TestUserLevelInfoModel:
    def test_construction(self):
        model = UserLevelInfoModel(xp=500, level=3, xp_needed=100, custom_background="bg.png")
        assert model.xp == 500
        assert model.custom_background == "bg.png"


class TestLevelRolesGroupModel:
    def test_construction(self):
        model = LevelRolesGroupModel(level=5, role_ids=[ROLE_ID])
        assert model.level == 5
        assert model.role_ids == [ROLE_ID]


class TestTwitchUserModel:
    def test_from_api_response(self):
        data = {
            "id": "123",
            "login": "test",
            "display_name": "Test",
            "type": "",
            "broadcaster_type": "",
            "description": "",
            "profile_image_url": "",
            "offline_image_url": "",
            "view_count": "0",
            "created_at": "2020-01-01T00:00:00Z",
        }
        model = TwitchUserModel.from_api_response(data)
        assert model.login == "test"

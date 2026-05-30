"""Parametrized iter_rows coverage for all models with iter_rows."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

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
    WarningModel,
    WelcomeChannelModel,
    XpBoostModel,
)
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, MESSAGE_ID, ROLE_ID, USER_ID, _dt, giveaway_row, warning_row


def _dt_local() -> datetime:
    return datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


ITER_ROW_CASES = [
    (GiveawayModel, giveaway_row()),
    (GiveawayChannelRequirementModel, (CHANNEL_ID, 3)),
    (GiveawayBlacklistEntryModel, (USER_ID, "reason")),
    (
        ReportModel,
        (1, GUILD_ID, USER_ID, USER_ID, "r", 1, True, 2, USER_ID, False, None, None),
    ),
    (
        ScheduledMessageModel,
        (1, GUILD_ID, CHANNEL_ID, USER_ID, "hi", _dt_local(), None, None, None, None, _dt_local()),
    ),
    (TwitchOnlineNotificationModel, (1, CHANNEL_ID, GUILD_ID, "uuid", "name", None)),
    (TriggerMessageModel, (1, GUILD_ID, "t", "r", True)),
    (TriggerMessageChannelModel, (GUILD_ID, CHANNEL_ID, 1)),
    (TicketMessageModel, (1, GUILD_ID, CHANNEL_ID, None, None, None, None, None)),
    (TicketModel, (GUILD_ID, USER_ID, 1, False, None, None, CHANNEL_ID, 1)),
    (AISituationModel, (USER_ID, None, None, _dt_local(), 0.7, 1.0, 0.0, 0.0, True)),
    (WarningModel, warning_row()),
    (DetailedWarningModel, (1, "r", _dt_local(), None, USER_ID)),
    (XpBoostModel, (1.0, False)),
    (BlacklistEntryModel, (USER_ID, None)),
    (LevelRoleModel, (5, ROLE_ID)),
    (DynamicSlowmodeModel, (GUILD_ID, CHANNEL_ID, 5, 10, 60, None)),
    (AfkMessageModel, (MESSAGE_ID, CHANNEL_ID)),
    (LogBlacklistEntryModel, (GUILD_ID, USER_ID)),
    (WelcomeChannelModel, (CHANNEL_ID, GUILD_ID, None, None)),
    (LeaveChannelModel, (CHANNEL_ID, GUILD_ID, None, None)),
    (DynamicSlowmodeMessageModel, (1, CHANNEL_ID, MESSAGE_ID, _dt_local())),
    (TokenOverviewModel, (1, 2, 3, 4)),
    (LogEnableModel, (GUILD_ID, *([True] * 24))),
    (ClaimedBoosterChannelModel, (USER_ID, CHANNEL_ID, GUILD_ID)),
    (ClaimedBoosterRoleModel, (USER_ID, ROLE_ID, GUILD_ID)),
    (BlockedReporterModel, (GUILD_ID, USER_ID)),
    (LevelLeaderboardEntryModel, (USER_ID, 100)),
    (ChannelOverwriteModel, (ROLE_ID, "{}")),
]


class TestAllModelIterRows:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("model_cls,row", ITER_ROW_CASES, ids=[c[0].__name__ for c in ITER_ROW_CASES])
    async def test_iter_rows_yields_model(self, model_cls, row):
        async def fake_iter(_query, _params=None):
            yield row

        with patch("api.execute_query_iter", side_effect=fake_iter):
            results = [item async for item in model_cls.iter_rows("SELECT 1")]

        assert len(results) == 1
        assert isinstance(results[0], model_cls)


class TestLogEnableCoerceNonDict:
    def test_coerce_passes_through_model_instance(self):
        base = LogEnableModel(guild_id=GUILD_ID, member_join=True)
        revalidated = LogEnableModel.model_validate(base)
        assert revalidated.member_join is True
        assert revalidated.guild_id == GUILD_ID

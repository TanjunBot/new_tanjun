from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from models import BlockedReporterModel, ReportEvidenceModel, ReportModActionModel, ReportModel
from services.report_service import ReportCreateParams, ReportFilter, ReportService
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID

OTHER_USER = "22222222222222222"
THIRD_USER = "33333333333333333"


async def _async_rows(*rows):
    for row in rows:
        yield row


class TestReportService:
    @pytest.mark.asyncio
    async def test_create_user_report(self):
        with patch("services.report_service.execute_insert_and_get_id", AsyncMock(return_value=5)):
            rid = await ReportService.create(
                ReportCreateParams(guild_id=GUILD_ID, user_id=OTHER_USER, reporter_id=THIRD_USER, reason="spam")
            )
        assert rid == 5

    @pytest.mark.asyncio
    async def test_create_moderator_report(self):
        with patch("services.report_service.execute_insert_and_get_id", AsyncMock(return_value=6)):
            rid = await ReportService.create(
                ReportCreateParams(
                    guild_id=GUILD_ID,
                    user_id=OTHER_USER,
                    reporter_id=THIRD_USER,
                    reason="spam",
                    is_moderator=True,
                )
            )
        assert rid == 6

    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        with patch("services.report_service.execute_query", AsyncMock(return_value=[])):
            old = await ReportService.update_status(GUILD_ID, "99", "investigating")
        assert old is None

    @pytest.mark.asyncio
    async def test_update_status_success(self):
        with (
            patch("services.report_service.execute_query", AsyncMock(return_value=[("pending",)])),
            patch("services.report_service.execute_action", AsyncMock()) as action,
        ):
            old = await ReportService.update_status(
                GUILD_ID, "5", "investigating", updated_by=USER_ID, note="ok"
            )
        assert old == "pending"
        action.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_anonymous_and_delete(self):
        with patch("services.report_service.execute_action", AsyncMock()) as action:
            await ReportService.set_anonymous(GUILD_ID, "5", True)
            await ReportService.delete(GUILD_ID, "5")
        assert action.await_count == 4

    @pytest.mark.asyncio
    async def test_evidence_crud(self):
        with (
            patch("services.report_service.execute_insert_and_get_id", AsyncMock(return_value=10)),
            patch(
                "services.report_service.ReportEvidenceModel.iter_rows",
                side_effect=lambda q, p: _async_rows(
                    ReportEvidenceModel(
                        id=10,
                        guild_id=GUILD_ID,
                        report_id=5,
                        url="http://x",
                        filename="f",
                        uploaded_by=THIRD_USER,
                        uploaded_at=1,
                    )
                ),
            ),
            patch("services.report_service.execute_action", AsyncMock()),
        ):
            eid = await ReportService.add_evidence(GUILD_ID, "5", "http://x", "f.png", THIRD_USER)
            rows = await ReportService.get_evidence(GUILD_ID, "5")
            await ReportService.delete_evidence(GUILD_ID, eid)
        assert eid == 10
        assert len(rows) == 1

    @pytest.mark.asyncio
    async def test_mod_actions(self):
        with (
            patch("services.report_service.execute_insert_and_get_id", AsyncMock(return_value=11)),
            patch(
                "services.report_service.ReportModActionModel.iter_rows",
                side_effect=lambda q, p: _async_rows(
                    ReportModActionModel(
                        id=11,
                        guild_id=GUILD_ID,
                        report_id=5,
                        action_type="ban",
                        target_id=OTHER_USER,
                        performed_by=THIRD_USER,
                        details=None,
                        created_at=1,
                    )
                ),
            ),
        ):
            mid = await ReportService.add_mod_action(GUILD_ID, "5", "ban", OTHER_USER, THIRD_USER)
            actions = await ReportService.get_mod_actions(GUILD_ID, "5")
        assert mid == 11
        assert actions[0].action_type == "ban"

    @pytest.mark.asyncio
    async def test_anonymity_settings(self):
        with (
            patch("services.report_service.execute_query", AsyncMock(return_value=[])),
            patch("services.report_service.execute_action", AsyncMock()) as action,
        ):
            await ReportService.set_anonymity_setting(GUILD_ID, True)
        action.assert_awaited_once()
        with patch("services.report_service.execute_query", AsyncMock(return_value=[(1,)])):
            assert await ReportService.get_anonymity_setting(GUILD_ID) is True

    @pytest.mark.asyncio
    async def test_anonymity_settings_update_existing(self):
        with (
            patch("services.report_service.execute_query", AsyncMock(return_value=[(GUILD_ID,)])),
            patch("services.report_service.execute_action", AsyncMock()) as action,
        ):
            await ReportService.set_anonymity_setting(GUILD_ID, False)
        action.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_notification_optout(self):
        with patch("services.report_service.execute_action", AsyncMock()) as action:
            await ReportService.set_notification_optout(GUILD_ID, THIRD_USER, True)
            await ReportService.set_notification_optout(GUILD_ID, THIRD_USER, False)
        assert action.await_count == 2
        with patch("services.report_service.execute_query", AsyncMock(return_value=[(1,)])):
            assert await ReportService.has_opted_out_of_notifications(GUILD_ID, THIRD_USER) is True

    @pytest.mark.asyncio
    async def test_blocked_reporters_and_channel(self):
        with (
            patch("services.report_service.execute_action", AsyncMock()) as action,
            patch(
                "services.report_service.BlockedReporterModel.iter_rows",
                side_effect=lambda q, p: _async_rows(
                    BlockedReporterModel(guild_id=GUILD_ID, user_id=THIRD_USER)
                ),
            ),
            patch("services.report_service.execute_query", AsyncMock(return_value=[(CHANNEL_ID,)])),
        ):
            await ReportService.block_reporter(GUILD_ID, THIRD_USER)
            await ReportService.unblock_reporter(GUILD_ID, THIRD_USER)
            blocked = await ReportService.get_blocked_reporters(GUILD_ID)
            await ReportService.set_channel(GUILD_ID, CHANNEL_ID)
            assert await ReportService.get_channel(GUILD_ID) == CHANNEL_ID
            await ReportService.remove_channel(GUILD_ID)
        assert blocked[0].user_id == THIRD_USER
        assert action.await_count >= 4

    @pytest.mark.asyncio
    async def test_get_reports_with_filter(self):
        with patch(
            "services.report_service.ReportModel.iter_rows",
            side_effect=lambda q, p: _async_rows(
                ReportModel(
                    id=1,
                    guild_id=GUILD_ID,
                    user_id=OTHER_USER,
                    reporter_id=THIRD_USER,
                    reason="spam",
                    created_at=1,
                    status="pending",
                    status_updated_at=None,
                    status_updated_by=None,
                    status_note=None,
                    anonymous=False,
                )
            ),
        ):
            rows = await ReportService.get(ReportFilter(guild_id=GUILD_ID, status="pending"))
        assert rows[0].reason == "spam"

    @pytest.mark.asyncio
    async def test_get_by_reporter_and_by_id(self):
        report = ReportModel(
            id=7,
            guild_id=GUILD_ID,
            user_id=OTHER_USER,
            reporter_id=THIRD_USER,
            reason="spam",
            created_at=1,
            status="pending",
            status_updated_at=None,
            status_updated_by=None,
            status_note=None,
            anonymous=False,
        )
        with patch(
            "services.report_service.ReportModel.iter_rows",
            side_effect=lambda q, p: _async_rows(report),
        ):
            by_reporter = await ReportService.get_by_reporter(GUILD_ID, THIRD_USER)
            by_id = await ReportService.get_by_id(GUILD_ID, "7")
        assert by_reporter[0].id == 7
        assert by_id is not None
        assert by_id.id == 7

    @pytest.mark.asyncio
    async def test_is_blocked(self):
        with patch("services.report_service.execute_query", AsyncMock(return_value=[(1,)])):
            assert await ReportService.is_blocked(GUILD_ID, THIRD_USER) is True

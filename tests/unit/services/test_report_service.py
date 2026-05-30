"""Tests for services/report_service.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from models import BlockedReporterModel, ReportModel
from services.report_service import ReportCreateParams, ReportFilter, ReportService, report_service
from tests.helpers.factories import GUILD_ID, USER_ID


REPORTER_ID = "22222222222222222"


def _report_row(
    *,
    accepted: int = 0,
    resolved: int = 0,
    report_id: int = 1,
):
    return (
        report_id,
        GUILD_ID,
        USER_ID,
        REPORTER_ID,
        "spam reason",
        1718452800,
        accepted,
        None,
        None,
        resolved,
        None,
        None,
    )


@pytest.fixture
def service() -> ReportService:
    return ReportService()


class TestReportCreateParams:
    def test_defaults(self):
        params = ReportCreateParams(
            guild_id=GUILD_ID, user_id=USER_ID, reporter_id=REPORTER_ID, reason="bad"
        )
        assert params.is_moderator is False

    def test_moderator_flag(self):
        params = ReportCreateParams(
            guild_id=GUILD_ID,
            user_id=USER_ID,
            reporter_id=REPORTER_ID,
            reason="bad",
            is_moderator=True,
        )
        assert params.is_moderator is True


class TestReportServiceCreate:
    @pytest.mark.asyncio
    async def test_create_regular(self, service: ReportService):
        with patch("services.report_service.execute_insert_and_get_id", new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = 42
            params = ReportCreateParams(
                guild_id=GUILD_ID, user_id=USER_ID, reporter_id=REPORTER_ID, reason="spam"
            )
            result = await service.create(params)
        assert result == 42
        query = mock_insert.await_args[0][0]
        assert "accepted" not in query

    @pytest.mark.asyncio
    async def test_create_moderator(self, service: ReportService):
        with patch("services.report_service.execute_insert_and_get_id", new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = 99
            params = ReportCreateParams(
                guild_id=GUILD_ID,
                user_id=USER_ID,
                reporter_id=REPORTER_ID,
                reason="spam",
                is_moderator=True,
            )
            result = await service.create(params)
        assert result == 99
        query = mock_insert.await_args[0][0]
        assert "accepted_at" in query


class TestReportServiceGet:
    @pytest.mark.asyncio
    async def test_get_by_guild_only(self, service: ReportService):
        async def fake_iter(*args, **kwargs):
            yield ReportModel.from_row(_report_row())

        with patch.object(ReportModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await service.get(ReportFilter(guild_id=GUILD_ID))
        assert len(result) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("status", "fragment"),
        [
            ("PENDING", "accepted = 0 AND resolved = 0"),
            ("ACCEPTED", "accepted = 1"),
            ("RESOLVED", "resolved = 1"),
            ("REJECTED", "accepted = 0 AND resolved = 1"),
        ],
    )
    async def test_get_with_status_filter(self, service: ReportService, status: str, fragment: str):
        captured: list[str] = []

        async def fake_iter(query, params):
            captured.append(query)
            yield ReportModel.from_row(_report_row())

        with patch.object(ReportModel, "iter_rows", side_effect=fake_iter):
            await service.get(ReportFilter(guild_id=GUILD_ID, status=status))
        assert fragment in captured[0]

    @pytest.mark.asyncio
    async def test_get_with_user_id(self, service: ReportService):
        captured: list[tuple] = []

        async def fake_iter(query, params):
            captured.append((query, params))
            yield ReportModel.from_row(_report_row())

        with patch.object(ReportModel, "iter_rows", side_effect=fake_iter):
            await service.get(ReportFilter(guild_id=GUILD_ID, user_id=USER_ID))
        assert "user_id = %s" in captured[0][0]
        assert USER_ID in captured[0][1]

    @pytest.mark.asyncio
    async def test_get_with_reporter_id(self, service: ReportService):
        captured: list[tuple] = []

        async def fake_iter(query, params):
            captured.append((query, params))
            yield ReportModel.from_row(_report_row())

        with patch.object(ReportModel, "iter_rows", side_effect=fake_iter):
            await service.get(ReportFilter(guild_id=GUILD_ID, reporter_id=REPORTER_ID))
        assert "reporterId = %s" in captured[0][0]

    @pytest.mark.asyncio
    async def test_get_by_reporter(self, service: ReportService):
        async def fake_iter(*args, **kwargs):
            yield ReportModel.from_row(_report_row())

        with patch.object(ReportModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await service.get_by_reporter(GUILD_ID, REPORTER_ID)
        assert len(result) == 1


class TestReportServiceActions:
    @pytest.mark.asyncio
    async def test_accept(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.accept(GUILD_ID, 5, REPORTER_ID)
            assert "accepted = 1" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_reject(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.reject(GUILD_ID, 5, REPORTER_ID)
            query = mock_exec.await_args[0][0]
            assert "resolved = 2" in query

    @pytest.mark.asyncio
    async def test_resolve(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.resolve(GUILD_ID, 5)
            assert "resolved = 1" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_delete(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.delete(GUILD_ID, 5)
            assert "DELETE FROM reports" in mock_exec.await_args[0][0]


class TestReportServiceBlockedReporters:
    @pytest.mark.asyncio
    async def test_block_reporter(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.block_reporter(GUILD_ID, REPORTER_ID)
            assert "INSERT INTO blockedReporters" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_unblock_reporter(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.unblock_reporter(GUILD_ID, REPORTER_ID)
            assert "DELETE FROM blockedReporters" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_blocked_reporters(self, service: ReportService):
        async def fake_iter(*args, **kwargs):
            yield BlockedReporterModel.from_row((GUILD_ID, REPORTER_ID))

        with patch.object(BlockedReporterModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await service.get_blocked_reporters(GUILD_ID)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_is_blocked_true(self, service: ReportService):
        with patch("services.report_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(1,)]
            assert await service.is_blocked(GUILD_ID, REPORTER_ID) is True

    @pytest.mark.asyncio
    async def test_is_blocked_false(self, service: ReportService):
        with patch("services.report_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            assert await service.is_blocked(GUILD_ID, REPORTER_ID) is False


class TestReportServiceChannel:
    @pytest.mark.asyncio
    async def test_set_channel(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.set_channel(GUILD_ID, "99999999999999999")
            assert "INSERT INTO reportchannel" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_channel_found(self, service: ReportService):
        with patch("services.report_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("99999999999999999",)]
            result = await service.get_channel(GUILD_ID)
        assert result == "99999999999999999"

    @pytest.mark.asyncio
    async def test_get_channel_none(self, service: ReportService):
        with patch("services.report_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await service.get_channel(GUILD_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_channel(self, service: ReportService):
        with patch("services.report_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.remove_channel(GUILD_ID)
            assert "DELETE FROM reportchannel" in mock_exec.await_args[0][0]


class TestReportServiceSingleton:
    def test_module_singleton(self):
        assert isinstance(report_service, ReportService)

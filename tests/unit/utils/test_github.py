"""Tests for utils/github.py GitHub issue helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import discord
import pytest

from utils.github import (
    _recent_reports,
    addFeedback,
    begin_missing_localization_capture,
    cleanup_captured_missing_localization_issues,
    end_missing_localization_capture,
    missingLocalization,
    report_bot_exception,
    report_bot_exception_sync,
    should_report_exception,
)


@pytest.fixture(autouse=True)
def _clear_exception_dedup_cache() -> None:
    _recent_reports.clear()
    yield
    _recent_reports.clear()


class TestShouldReportException:
    def test_reports_generic_exception(self):
        assert should_report_exception(RuntimeError("boom")) is True

    def test_skips_forbidden(self):
        assert should_report_exception(discord.Forbidden(MagicMock(), "missing perms")) is False

    def test_skips_not_found(self):
        assert should_report_exception(discord.NotFound(MagicMock(), "missing")) is False

    def test_skips_client_connection_reset(self):
        class ClientConnectionResetError(Exception):
            pass

        assert should_report_exception(ClientConnectionResetError("Cannot write to closing transport")) is False

    def test_skips_task_already_launched(self):
        assert should_report_exception(RuntimeError("Task is already launched and is not completed.")) is False

    def test_skips_command_not_found(self):
        class CommandNotFound(Exception):
            __module__ = "discord.ext.commands.errors"

        assert should_report_exception(CommandNotFound('Command "synnc" is not found')) is False

    def test_skips_discord_server_error(self):
        assert should_report_exception(discord.DiscordServerError(MagicMock(), "503 Service Unavailable")) is False

    def test_skips_http_503(self):
        resp = MagicMock()
        resp.status = 503
        exc = discord.HTTPException(resp, "Service Unavailable")
        assert should_report_exception(exc) is False

    def test_skips_ws_server_handshake_error(self):
        request_info = MagicMock()
        request_info.real_url = "wss://gateway-us-east1-b.discord.gg/?v=10&encoding=json&compress=zlib-stream"
        exc = aiohttp.WSServerHandshakeError(
            request_info=request_info,
            history=(),
            status=520,
            message="Invalid response status",
        )
        assert should_report_exception(exc) is False

    def test_skips_mysql_operational_error_lost_connection(self):
        class OperationalError(Exception):
            pass

        exc = OperationalError("(2013, 'Lost connection to MySQL server during query')")
        assert should_report_exception(exc) is False

    def test_skips_incomplete_read_error(self):
        import asyncio

        exc = asyncio.IncompleteReadError(b"", 4)
        assert should_report_exception(exc) is False


class TestReportBotException:
    @pytest.mark.asyncio
    async def test_reports_via_run_blocking(self):
        with patch("utils.github.run_blocking", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = None
            await report_bot_exception(RuntimeError("boom"), source="test")
            mock_run.assert_called_once()

    def test_sync_reports_when_token_present(self):
        with patch("utils.github.GithubAuthToken", "token"), patch("utils.github.Github") as mock_github:
            mock_repo = MagicMock()
            mock_g = MagicMock()
            mock_g.get_repo.return_value = mock_repo
            mock_g.search_issues.return_value.totalCount = 0
            mock_github.return_value = mock_g
            report_bot_exception_sync(RuntimeError("boom"), source="test", context={"command": "/ping"})
            mock_repo.create_issue.assert_called_once()
            body = mock_repo.create_issue.call_args[1]["body"]
            assert "**Fingerprint:**" in body

    def test_dedup_prevents_duplicate_reports(self):
        with patch("utils.github.GithubAuthToken", "token"), patch("utils.github.Github") as mock_github:
            mock_repo = MagicMock()
            mock_g = MagicMock()
            mock_g.get_repo.return_value = mock_repo
            mock_g.search_issues.return_value.totalCount = 0
            mock_github.return_value = mock_g
            exc = RuntimeError("same error")
            report_bot_exception_sync(exc, source="first")
            report_bot_exception_sync(exc, source="second")
            assert mock_repo.create_issue.call_count == 1

    def test_sync_skips_when_open_issue_exists_on_github(self):
        with patch("utils.github.GithubAuthToken", "token"), patch("utils.github.Github") as mock_github:
            mock_repo = MagicMock()
            mock_g = MagicMock()
            mock_g.get_repo.return_value = mock_repo
            mock_g.search_issues.return_value.totalCount = 1
            mock_github.return_value = mock_g
            report_bot_exception_sync(RuntimeError("boom"), source="test")
            mock_repo.create_issue.assert_not_called()


class TestMissingLocalization:
    @pytest.mark.asyncio
    async def test_creates_issue_via_run_blocking(self):
        with patch("utils.github.run_blocking", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = None
            await missingLocalization("de-DE", "test.key")
            mock_run.assert_called_once()
            args = mock_run.call_args[0]
            assert args[1] == "de-DE"
            assert args[2] == "test.key"


class TestAddFeedback:
    @pytest.mark.asyncio
    async def test_creates_feedback_issue(self):
        with patch("utils.github.run_blocking", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = None
            await addFeedback("Great bot!", "TestUser")
            mock_run.assert_called_once()
            args = mock_run.call_args[0]
            assert args[1] == "Great bot!"
            assert args[2] == "TestUser"


class TestSyncHelpers:
    def test_sync_create_missing_localization_issue(self):
        from utils.github import _sync_create_missing_localization_issue

        mock_repo = MagicMock()
        mock_label = MagicMock()
        mock_repo.get_label.return_value = mock_label
        mock_g = MagicMock()
        mock_g.get_repo.return_value = mock_repo
        mock_g.search_issues.return_value.totalCount = 0

        with patch("utils.github.GithubAuthToken", "token"), patch("utils.github.Github", return_value=mock_g):
            _sync_create_missing_localization_issue("fr-FR", "commands.test.title")

        mock_repo.create_issue.assert_called_once()
        call_kwargs = mock_repo.create_issue.call_args[1]
        assert "fr-FR" in call_kwargs["body"]
        assert "commands.test.title" in call_kwargs["body"]
        assert "commands.test.title" in call_kwargs["title"]

    def test_sync_create_missing_localization_issue_skips_existing(self):
        from utils.github import _sync_create_missing_localization_issue

        mock_repo = MagicMock()
        mock_g = MagicMock()
        mock_g.get_repo.return_value = mock_repo
        mock_g.search_issues.return_value.totalCount = 1

        with patch("utils.github.GithubAuthToken", "token"), patch("utils.github.Github", return_value=mock_g):
            _sync_create_missing_localization_issue("fr-FR", "commands.test.title")

        mock_repo.create_issue.assert_not_called()

    def test_sync_create_missing_localization_issue_skips_without_token(self):
        from utils.github import _sync_create_missing_localization_issue

        with patch("utils.github.GithubAuthToken", ""), patch("utils.github.Github") as mock_github:
            _sync_create_missing_localization_issue("fr-FR", "commands.test.title")

        mock_github.assert_not_called()

    def test_sync_create_missing_localization_issue_skips_when_translation_exists(self):
        from utils.github import _sync_create_missing_localization_issue

        with (
            patch("utils.github.GithubAuthToken", "token"),
            patch("utils.github.Github") as mock_github,
            patch("utils.github._missing_localization_resolved", return_value=True),
        ):
            _sync_create_missing_localization_issue("fr", "admin.emoji.name")

        mock_github.assert_not_called()

    def test_sync_create_feedback_issue(self):
        from utils.github import _sync_create_feedback_issue

        mock_repo = MagicMock()
        mock_repo.get_label.return_value = MagicMock()
        mock_g = MagicMock()
        mock_g.get_repo.return_value = mock_repo

        with patch("utils.github.Github", return_value=mock_g):
            _sync_create_feedback_issue("Nice feature", "Alice")

        mock_repo.create_issue.assert_called_once()
        assert "Alice" in mock_repo.create_issue.call_args[1]["body"]


class TestMissingLocalizationCleanup:
    @pytest.mark.asyncio
    async def test_cleanup_captured_missing_localization_issues_closes_created_issues(self):
        issue = MagicMock()
        issue.number = 123
        issue_to_close = MagicMock()
        mock_repo = MagicMock()
        mock_repo.create_issue.return_value = issue
        mock_repo.get_issue.return_value = issue_to_close
        mock_g = MagicMock()
        mock_g.get_repo.return_value = mock_repo
        mock_g.search_issues.return_value.totalCount = 0

        with (
            patch("utils.github.GithubAuthToken", "token"),
            patch("utils.github.Github", return_value=mock_g),
            patch("utils.github._missing_localization_resolved", return_value=False),
        ):
            begin_missing_localization_capture()
            from utils.github import _sync_create_missing_localization_issue

            _sync_create_missing_localization_issue("fr-FR", "commands.test.title")
            end_missing_localization_capture()
            closed = await cleanup_captured_missing_localization_issues()

        assert closed == 1
        issue_to_close.edit.assert_called_once_with(state="closed")

    @pytest.mark.asyncio
    async def test_cleanup_without_capture_does_nothing(self):
        begin_missing_localization_capture()
        end_missing_localization_capture()
        closed = await cleanup_captured_missing_localization_issues()
        assert closed == 0

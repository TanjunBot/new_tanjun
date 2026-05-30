"""Tests for utils/github.py GitHub issue helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils.github import addFeedback, missingLocalization


class TestMissingLocalization:
    @pytest.mark.asyncio
    async def test_creates_issue_via_run_blocking(self):
        with patch("utils.github.run_blocking", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = None
            await missingLocalization("de-DE")
            mock_run.assert_called_once()
            args = mock_run.call_args[0]
            assert args[1] == "de-DE"


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

        with patch("utils.github.Github", return_value=mock_g):
            _sync_create_missing_localization_issue("fr-FR")

        mock_repo.create_issue.assert_called_once()
        call_kwargs = mock_repo.create_issue.call_args[1]
        assert "fr-FR" in call_kwargs["body"]

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

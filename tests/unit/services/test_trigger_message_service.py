"""Tests for services/trigger_message_service.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from models import TriggerMessageChannelModel, TriggerMessageModel
from services.trigger_message_service import (
    TriggerMessageChannelAddParams,
    TriggerMessageCreateParams,
    TriggerMessageService,
    trigger_message_service,
)
from tests.helpers.factories import CHANNEL_ID, GUILD_ID


@pytest.fixture
def service() -> TriggerMessageService:
    return TriggerMessageService()


def _trigger_row(trigger: str = "hello", case_sensitive: bool = False, trigger_id: int = 1):
    return (trigger_id, GUILD_ID, trigger, "response text", case_sensitive)


def _channel_row(trigger_id: int = 1):
    return (GUILD_ID, CHANNEL_ID, trigger_id)


class TestTriggerMessageCreateParams:
    def test_valid_params(self):
        params = TriggerMessageCreateParams(guild_id=GUILD_ID, trigger="hi", response="there", case_sensitive=True)
        assert params.trigger == "hi"
        assert params.case_sensitive is True

    def test_empty_trigger_rejected(self):
        with pytest.raises(ValidationError):
            TriggerMessageCreateParams(guild_id=GUILD_ID, trigger="", response="x")

    def test_empty_response_rejected(self):
        with pytest.raises(ValidationError):
            TriggerMessageCreateParams(guild_id=GUILD_ID, trigger="x", response="")


class TestTriggerMessageChannelAddParams:
    def test_valid_params(self):
        params = TriggerMessageChannelAddParams(guild_id=GUILD_ID, channel_id=CHANNEL_ID, trigger_id=5)
        assert params.trigger_id == 5


class TestTriggerMessageServiceCrud:
    @pytest.mark.asyncio
    async def test_create(self, service: TriggerMessageService):
        with patch("services.trigger_message_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.create(GUILD_ID, "trigger", "response", True)
            mock_exec.assert_awaited_once()
            query, params = mock_exec.await_args[0]
            assert "INSERT INTO triggerMessages" in query
            assert params == (GUILD_ID, "trigger", "response", True)

    @pytest.mark.asyncio
    async def test_delete(self, service: TriggerMessageService):
        with patch("services.trigger_message_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.delete(GUILD_ID, 7)
            assert "DELETE FROM triggerMessages" in mock_exec.await_args[0][0]
            assert mock_exec.await_args[0][1] == (GUILD_ID, 7)

    @pytest.mark.asyncio
    async def test_get_all(self, service: TriggerMessageService):
        async def fake_iter(*args, **kwargs):
            yield TriggerMessageModel.from_row(_trigger_row())

        with patch.object(TriggerMessageModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await service.get_all(GUILD_ID)
        assert len(result) == 1
        assert result[0].trigger == "hello"


class TestTriggerMessageServiceChannels:
    @pytest.mark.asyncio
    async def test_add_channel(self, service: TriggerMessageService):
        with patch("services.trigger_message_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.add_channel(GUILD_ID, CHANNEL_ID, 3)
            query, params = mock_exec.await_args[0]
            assert "INSERT INTO triggerMessagesChannel" in query
            assert params == (GUILD_ID, CHANNEL_ID, 3)

    @pytest.mark.asyncio
    async def test_remove_channel(self, service: TriggerMessageService):
        with patch("services.trigger_message_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.remove_channel(GUILD_ID, CHANNEL_ID, 3)
            assert "DELETE FROM triggerMessagesChannel" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_trigger_channels(self, service: TriggerMessageService):
        async def fake_iter(*args, **kwargs):
            yield TriggerMessageChannelModel.from_row(_channel_row())

        with patch.object(TriggerMessageChannelModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await service.get_trigger_channels(GUILD_ID, 1)
        assert len(result) == 1
        assert result[0].channel_id == CHANNEL_ID

    @pytest.mark.asyncio
    async def test_get_channel_triggers(self, service: TriggerMessageService):
        async def fake_iter(*args, **kwargs):
            yield TriggerMessageChannelModel.from_row(_channel_row(2))

        with patch.object(TriggerMessageChannelModel, "iter_rows", side_effect=lambda q, p: fake_iter()):
            result = await service.get_channel_triggers(GUILD_ID, CHANNEL_ID)
        assert len(result) == 1
        assert result[0].trigger_id == 2


class TestTriggerMessageServiceMatch:
    @pytest.mark.asyncio
    async def test_exact_match_case_insensitive(self, service: TriggerMessageService):
        row = _trigger_row("Hello", False)
        with patch("services.trigger_message_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await service.match(GUILD_ID, "hello", CHANNEL_ID)
        assert result is not None
        assert result.trigger == "Hello"

    @pytest.mark.asyncio
    async def test_exact_match_case_sensitive_match(self, service: TriggerMessageService):
        row = _trigger_row("Hello", True)
        with patch("services.trigger_message_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await service.match(GUILD_ID, "Hello", CHANNEL_ID)
        assert result is not None

    @pytest.mark.asyncio
    async def test_exact_match_case_sensitive_mismatch_falls_through(self, service: TriggerMessageService):
        exact_row = _trigger_row("Hello", True)
        like_row = _trigger_row("hello", False, 2)

        async def side_effect(query, params):
            if "`trigger` = %s" in query:
                return [exact_row]
            return [like_row]

        with patch("services.trigger_message_service.execute_query", side_effect=side_effect):
            result = await service.match(GUILD_ID, "hello", CHANNEL_ID)
        assert result is not None
        assert result.id == 2

    @pytest.mark.asyncio
    async def test_like_exact_match_case_insensitive(self, service: TriggerMessageService):
        like_row = _trigger_row("World", False)

        async def side_effect(query, params):
            if "`trigger` = %s" in query:
                return []
            return [like_row]

        with patch("services.trigger_message_service.execute_query", side_effect=side_effect):
            result = await service.match(GUILD_ID, "world", CHANNEL_ID)
        assert result is not None
        assert result.trigger == "World"

    @pytest.mark.asyncio
    async def test_like_partial_match_case_insensitive(self, service: TriggerMessageService):
        like_row = _trigger_row("ping", False)

        async def side_effect(query, params):
            if "`trigger` = %s" in query:
                return []
            return [like_row]

        with patch("services.trigger_message_service.execute_query", side_effect=side_effect):
            result = await service.match(GUILD_ID, "something ping something", CHANNEL_ID)
        assert result is not None

    @pytest.mark.asyncio
    async def test_like_partial_match_case_sensitive(self, service: TriggerMessageService):
        like_row = _trigger_row("Ping", True)

        async def side_effect(query, params):
            if "`trigger` = %s" in query:
                return []
            return [like_row]

        with patch("services.trigger_message_service.execute_query", side_effect=side_effect):
            result = await service.match(GUILD_ID, "say Ping now", CHANNEL_ID)
        assert result is not None

    @pytest.mark.asyncio
    async def test_like_partial_case_sensitive_no_match(self, service: TriggerMessageService):
        like_row = _trigger_row("Ping", True)

        async def side_effect(query, params):
            if "`trigger` = %s" in query:
                return []
            return [like_row]

        with patch("services.trigger_message_service.execute_query", side_effect=side_effect):
            result = await service.match(GUILD_ID, "say ping now", CHANNEL_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_no_results(self, service: TriggerMessageService):
        with patch("services.trigger_message_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await service.match(GUILD_ID, "missing", CHANNEL_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_skips_empty_rows_in_like_results(self, service: TriggerMessageService):
        like_row = _trigger_row("found", False)

        async def side_effect(query, params):
            if "`trigger` = %s" in query:
                return []
            return [None, like_row]

        with patch("services.trigger_message_service.execute_query", side_effect=side_effect):
            result = await service.match(GUILD_ID, "found", CHANNEL_ID)
        assert result is not None

    @pytest.mark.asyncio
    async def test_exact_empty_result_falls_to_like(self, service: TriggerMessageService):
        like_row = _trigger_row("target", False)

        call_count = 0

        async def side_effect(query, params):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return []
            return [like_row]

        with patch("services.trigger_message_service.execute_query", side_effect=side_effect):
            result = await service.match(GUILD_ID, "target", CHANNEL_ID)
        assert result is not None
        assert call_count == 2


class TestTriggerMessageServiceSingleton:
    def test_module_singleton(self):
        assert isinstance(trigger_message_service, TriggerMessageService)

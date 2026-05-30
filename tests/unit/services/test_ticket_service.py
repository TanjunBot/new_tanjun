"""Tests for services/ticket_service.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services.ticket_service import TicketMessageConfig, TicketService
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID


class TestTicketService:
    @pytest.mark.asyncio
    async def test_create_config(self):
        params = TicketMessageConfig(
            guild_id=GUILD_ID,
            channel_id=CHANNEL_ID,
            introduction="Welcome",
            ping_role=None,
            name="Support",
            description="Help desk",
            summary_channel_id=None,
        )
        with patch("services.ticket_service.execute_insert_and_get_id", new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = 1
            result = await TicketService.create_config(params)
        assert result == 1

    @pytest.mark.asyncio
    async def test_delete_config(self):
        with patch("services.ticket_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await TicketService.delete_config(GUILD_ID, 1)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_open_ticket(self):
        with patch("services.ticket_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await TicketService.open(GUILD_ID, USER_ID, 1, CHANNEL_ID)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_ticket(self):
        with patch("services.ticket_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await TicketService.close(GUILD_ID, CHANNEL_ID, USER_ID)
            mock_exec.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_config_by_id(self):
        row = (1, GUILD_ID, CHANNEL_ID, None, None, "Support", None, None)
        with patch("services.ticket_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await TicketService.get_config(1)
        assert result is not None
        assert result.name == "Support"

    @pytest.mark.asyncio
    async def test_get_config_none(self):
        with patch("services.ticket_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await TicketService.get_config(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_channel(self):
        row = (GUILD_ID, USER_ID, 1700000000, False, None, None, CHANNEL_ID, 1)
        with patch("services.ticket_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await TicketService.get_by_channel(GUILD_ID, CHANNEL_ID)
        assert result is not None
        assert result.opener_id == USER_ID

    @pytest.mark.asyncio
    async def test_get_configs(self):
        from models import TicketMessageModel

        row = (1, GUILD_ID, CHANNEL_ID, None, None, "Support", None, None)

        async def fake_iter(*args, **kwargs):
            yield TicketMessageModel.from_row(row)

        with patch.object(TicketMessageModel, "iter_rows", side_effect=fake_iter):
            result = await TicketService.get_configs(GUILD_ID)
        assert len(result) == 1
        assert result[0].name == "Support"

    @pytest.mark.asyncio
    async def test_get_tickets(self):
        row = (GUILD_ID, USER_ID, 1700000000, False, None, None, CHANNEL_ID, 1)

        async def fake_iter(*args, **kwargs):
            from models import TicketModel

            yield TicketModel.from_row(row)

        from models import TicketModel

        with patch.object(TicketModel, "iter_rows", side_effect=fake_iter):
            result = await TicketService.get_tickets(GUILD_ID)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_by_config_and_channel(self):
        row = (GUILD_ID, USER_ID, 1700000000, False, None, None, CHANNEL_ID, 1)
        with patch("services.ticket_service.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [row]
            result = await TicketService.get_by_config_and_channel(GUILD_ID, 1, CHANNEL_ID)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_by_config_and_channel_none(self):
        with patch("services.ticket_service.execute_query", new_callable=AsyncMock, return_value=[]):
            result = await TicketService.get_by_config_and_channel(GUILD_ID, 1, CHANNEL_ID)
        assert result is None

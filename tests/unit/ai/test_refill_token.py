"""Tests for ai/refill_token.py."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai.refill_token import refill_ai_token


def _client_with_skus(skus):
    client = MagicMock()
    client.fetch_skus = AsyncMock(return_value=skus)
    return client


class TestRefillAiToken:
    @pytest.mark.asyncio
    async def test_skips_outside_refill_window(self):
        client = _client_with_skus([])
        with patch("ai.refill_token.datetime") as dt_mod:
            dt_mod.now.return_value = datetime(2024, 6, 15, 12, 30)
            await refill_ai_token(client)
        client.fetch_skus.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_refills_with_plus_sku_entitlements(self):
        plus_sku = MagicMock(name="Tanjun Plus")
        plus_sku.name = "Tanjun Plus"
        client = _client_with_skus([plus_sku])
        async def _iter_ents(*args, **kwargs):
            yield "ent1"
        client.entitlements = MagicMock()
        client.entitlements.return_value = _iter_ents()
        with (
            patch("ai.refill_token.datetime") as dt_mod,
            patch("ai.refill_token.AiService.refill", new=AsyncMock()) as refill_mock,
        ):
            dt_mod.now.return_value = datetime(2024, 1, 1, 0, 0)
            await refill_ai_token(client)
        client.fetch_skus.assert_awaited_once()
        client.entitlements.assert_called_once_with(skus=[plus_sku])
        refill_mock.assert_awaited_once_with(["ent1"])

    @pytest.mark.asyncio
    async def test_refills_without_sku_when_plus_missing(self):
        other_sku = MagicMock()
        other_sku.name = "Other SKU"
        client = _client_with_skus([other_sku])
        with (
            patch("ai.refill_token.datetime") as dt_mod,
            patch("ai.refill_token.AiService.refill", new=AsyncMock()) as refill_mock,
        ):
            dt_mod.now.return_value = datetime(2024, 2, 1, 0, 0)
            await refill_ai_token(client)
        refill_mock.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_refills_without_sku_when_no_skus(self):
        client = _client_with_skus([])
        with (
            patch("ai.refill_token.datetime") as dt_mod,
            patch("ai.refill_token.AiService.refill", new=AsyncMock()) as refill_mock,
        ):
            dt_mod.now.return_value = datetime(2024, 3, 1, 0, 0)
            await refill_ai_token(client)
        refill_mock.assert_awaited_once_with()
        client.entitlements.assert_not_called()

    @pytest.mark.asyncio
    async def test_refill_window_exact_match(self):
        client = _client_with_skus([])
        with (
            patch("ai.refill_token.datetime") as dt_mod,
            patch("ai.refill_token.AiService.refill", new=AsyncMock()) as refill_mock,
        ):
            dt_mod.now.return_value = datetime(2024, 12, 1, 0, 0)
            await refill_ai_token(client)
        client.fetch_skus.assert_awaited_once()
        refill_mock.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_selects_first_matching_plus_sku(self):
        plus_sku = MagicMock()
        plus_sku.name = "Tanjun Plus"
        client = _client_with_skus([plus_sku, MagicMock(name="Tanjun Plus 2")])
        async def _iter_empty(*args, **kwargs):
            if False:
                yield  # pragma: no cover
        client.entitlements = MagicMock()
        client.entitlements.return_value = _iter_empty()
        with (
            patch("ai.refill_token.datetime") as dt_mod,
            patch("ai.refill_token.AiService.refill", new=AsyncMock()) as refill_mock,
        ):
            dt_mod.now.return_value = datetime(2024, 4, 1, 0, 0)
            await refill_ai_token(client)
        refill_mock.assert_awaited_once_with([])

    @pytest.mark.asyncio
    async def test_one_minute_before_window_skips(self):
        client = _client_with_skus([])
        with patch("ai.refill_token.datetime") as dt_mod:
            dt_mod.now.return_value = datetime(2024, 5, 31, 23, 59)
            await refill_ai_token(client)
        client.fetch_skus.assert_not_awaited()

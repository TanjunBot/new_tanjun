"""Unit tests to verify pool connections are released."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import _get_cached_config, execute_batch, set_bot, transaction  # noqa: E402
from tests.helpers.db import make_mock_pool  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def reset_bot():
    set_bot(None)
    yield
    set_bot(None)


class TestPoolRelease:
    @pytest.mark.asyncio
    async def test_transaction_releases_connection(self):
        pool, _conn, _cursor = make_mock_pool()
        pool.release = MagicMock()
        set_bot(MagicMock(_pool=pool))

        async with transaction():
            pass

        pool.release.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_batch_releases_connection(self):
        pool, _conn, _cursor = make_mock_pool()
        pool.release = MagicMock()
        set_bot(MagicMock(_pool=pool))

        await execute_batch("INSERT INTO test (a) VALUES (%s)", [(1,), (2,)])

        pool.release.assert_called_once()

    @pytest.mark.asyncio
    async def test_cached_config_query_releases_connection(self):
        pool, _conn, cursor = make_mock_pool(fetchone=("123", 1, 2, None, 0, None, None, 60, 60))
        pool.release = MagicMock()
        set_bot(MagicMock(_pool=pool))

        await _get_cached_config("123", "active", False)

        pool.release.assert_called_once()

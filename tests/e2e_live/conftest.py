from __future__ import annotations

import pytest
import pytest_asyncio

from tests.helpers.live_discord.bot_process import ensure_e2e_bot_running, should_manage_bot_process
from tests.helpers.live_discord.readiness import live_e2e_skip_reason
from tests.helpers.live_discord.session import LiveGuildSession

pytestmark = [pytest.mark.live_discord, pytest.mark.timeout(300)]


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "live_discord: real Discord E2E (user token, bot token, Playwright session)",
    )
    config.addinivalue_line(
        "markers",
        "live_domain: domain-scoped live E2E subset (skipped in full-suite runs)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    import os

    reason = live_e2e_skip_reason()
    if reason is not None:
        skip = pytest.mark.skip(reason=reason)
        for item in items:
            if "/tests/e2e_live/" in str(item.fspath):
                item.add_marker(skip)
        return

    domain_only = os.getenv("TANJUN_E2E_DOMAIN_ONLY", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    for item in items:
        is_domain = item.get_closest_marker("live_domain") is not None
        is_full = item.get_closest_marker("live_full_suite") is not None
        if domain_only and is_full:
            item.add_marker(pytest.mark.skip(reason="TANJUN_E2E_DOMAIN_ONLY is set"))
        elif not domain_only and is_domain:
            item.add_marker(
                pytest.mark.skip(
                    reason="domain live tests skipped in full suite (set TANJUN_E2E_DOMAIN_ONLY=1)"
                )
            )


@pytest_asyncio.fixture(scope="session")
async def live_e2e_bot_process():
    process = await ensure_e2e_bot_running()
    yield process
    if process is not None:
        await process.stop()


@pytest_asyncio.fixture(scope="session")
async def live_guild_session(live_e2e_bot_process) -> LiveGuildSession:
    session = await LiveGuildSession.create(
        skip_api_command_ready_check=should_manage_bot_process()
        and live_e2e_bot_process is not None,
    )
    yield session
    await session.teardown()

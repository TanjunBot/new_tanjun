from __future__ import annotations

import os

import pytest
import pytest_asyncio

from tests.helpers.live_discord.bot_process import ensure_e2e_bot_running, should_manage_bot_process
from tests.helpers.live_discord.readiness import live_e2e_skip_reason
from tests.helpers.live_discord.session import LiveGuildSession

pytestmark = [pytest.mark.live_discord, pytest.mark.timeout(300)]

E2E_LIVE_SHARDS = (
    "admin",
    "utility",
    "math",
    "channel",
    "level",
    "logs",
    "games",
    "giveaway",
    "image",
    "ai",
    "minigames",
    "setup",
    "fun",
)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("e2e", "Live E2E")
    group.addoption(
        "--shard-id",
        type=int,
        default=None,
        help="0-based shard index; use with --num-shards=13 to match CI domain shards",
    )
    group.addoption(
        "--num-shards",
        type=int,
        default=None,
        help=f"Shard count; must be {len(E2E_LIVE_SHARDS)} for domain-based sharding",
    )


def _resolve_shard_domain(config: pytest.Config) -> str | None:
    shard_id = config.getoption("--shard-id")
    num_shards = config.getoption("--num-shards")
    if shard_id is None and num_shards is None:
        return None
    if shard_id is None or num_shards is None:
        raise pytest.UsageError("--shard-id and --num-shards must be used together")
    if shard_id < 0 or num_shards < 1 or shard_id >= num_shards:
        raise pytest.UsageError(f"invalid shard {shard_id} of {num_shards}")
    if num_shards != len(E2E_LIVE_SHARDS):
        raise pytest.UsageError(
            f"--num-shards must be {len(E2E_LIVE_SHARDS)} for domain sharding; got {num_shards}"
        )
    return E2E_LIVE_SHARDS[shard_id]


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "live_discord: real Discord E2E (user token, bot token, Playwright session)",
    )
    config.addinivalue_line(
        "markers",
        "live_domain: domain-scoped live E2E subset (skipped in full-suite runs)",
    )
    config.addinivalue_line(
        "markers",
        "live_full_suite: full live smoke matrix (skipped when TANJUN_E2E_DOMAIN_ONLY is set)",
    )
    shard_domain = _resolve_shard_domain(config)
    config._e2e_live_shard_domain = shard_domain
    if shard_domain is not None:
        os.environ.setdefault("TANJUN_E2E_DOMAIN_FILTER", shard_domain)


def _e2e_live_subdir(path: str) -> str | None:
    marker = "/tests/e2e_live/"
    if marker not in path:
        return None
    tail = path.split(marker, 1)[1]
    head = tail.split("/", 1)[0]
    if head.endswith(".py"):
        return None
    return head


def _deselect_items(config: pytest.Config, items: list[pytest.Item], deselected: list[pytest.Item]) -> None:
    if not deselected:
        return
    deselected_ids = {id(item) for item in deselected}
    items[:] = [item for item in items if id(item) not in deselected_ids]
    config.hook.pytest_deselected(items=deselected)


def pytest_report_header(config: pytest.Config) -> list[str]:
    shard_domain = getattr(config, "_e2e_live_shard_domain", None)
    if shard_domain is None:
        return []
    shard_id = config.getoption("--shard-id")
    return [f"live E2E shard {shard_id}/{len(E2E_LIVE_SHARDS)}: {shard_domain} (smoke matrix only)"]


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    reason = live_e2e_skip_reason()
    if reason is not None:
        skip = pytest.mark.skip(reason=reason)
        for item in items:
            if "/tests/e2e_live/" in str(item.fspath):
                item.add_marker(skip)
        return

    shard_domain = getattr(config, "_e2e_live_shard_domain", None)
    if shard_domain is not None:
        kept: list[pytest.Item] = []
        deselected: list[pytest.Item] = []
        for item in items:
            path = str(item.fspath)
            subdir = _e2e_live_subdir(path)
            if subdir == shard_domain:
                deselected.append(item)
                continue
            if path.endswith("/tests/e2e_live/test_commands_smoke_live.py"):
                kept.append(item)
                continue
            if "/tests/e2e_live/" in path:
                deselected.append(item)
                continue
            kept.append(item)
        _deselect_items(config, items, deselected)
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

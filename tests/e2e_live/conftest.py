import os

import pytest

pytestmark = pytest.mark.live_discord


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "live_discord: requires live Discord bot token")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("TANJUN_TEST_BOT_TOKEN"):
        return
    skip = pytest.mark.skip(reason="TANJUN_TEST_BOT_TOKEN not set")
    for item in items:
        item.add_marker(skip)

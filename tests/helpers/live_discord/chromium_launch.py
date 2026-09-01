from __future__ import annotations

from typing import TYPE_CHECKING

from tests.helpers.live_discord.timeouts import LiveE2ETimeouts

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Playwright

CHROMIUM_ARGS = (
    "--disable-external-intent-requests",
    "--no-first-run",
    "--no-default-browser-check",
)


def launch_live_e2e_browser(
    playwright: Playwright,
    *,
    headless: bool,
    auth_state_path: str,
    timeouts: LiveE2ETimeouts,
) -> tuple[Browser, BrowserContext]:
    browser = playwright.chromium.launch(
        headless=headless,
        args=list(CHROMIUM_ARGS),
    )
    context = browser.new_context(
        storage_state=auth_state_path,
        locale="en-US",
        viewport={"width": 1280, "height": 900},
    )
    context.set_default_timeout(timeouts.playwright_default_ms)
    context.set_default_navigation_timeout(timeouts.playwright_navigation_ms)
    return browser, context

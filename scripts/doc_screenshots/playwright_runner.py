from __future__ import annotations

import re
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

    from doc_screenshots.config import DocScreenshotConfig
    from doc_screenshots.manifest import ScreenshotShot

DISCORD_LOGIN_URL = "https://discord.com/login"
MESSAGE_INPUT_SELECTORS = (
    'div[role="textbox"][data-slate-editor="true"]',
    'div[aria-label^="Message #"]',
    'div[aria-label^="Nachricht #"]',
)
MESSAGE_LIST_SELECTOR = 'ol[data-list-id="chat-messages"]'
MESSAGE_ITEM_SELECTOR = 'li[id^="chat-messages-"]'


def _channel_url(guild_id: str, channel_id: str) -> str:
    return f"https://discord.com/channels/{guild_id}/{channel_id}"


def _find_message_input(page: Page) -> Locator:
    for selector in MESSAGE_INPUT_SELECTORS:
        loc = page.locator(selector).first
        if loc.count() > 0:
            return loc
    raise RuntimeError(
        "Could not find Discord message input. "
        "Discord may have changed its UI; update MESSAGE_INPUT_SELECTORS."
    )


def _message_items(page: Page) -> Locator:
    return page.locator(MESSAGE_ITEM_SELECTOR)


def _author_id_from_message(message: Locator) -> str | None:
    for selector in (
        'a[href*="/users/"]',
        'img[class*="avatar"][src*="/avatars/"]',
    ):
        link = message.locator(selector).first
        if link.count() == 0:
            continue
        href = link.get_attribute("href") or ""
        match = re.search(r"/users/(\d+)", href)
        if match:
            return match.group(1)
    header = message.locator('[id^="message-username-"]').first
    if header.count() > 0:
        uid = header.get_attribute("data-user-id")
        if uid:
            return uid
    return None


def _is_bot_message(message: Locator, bot_user_id: str) -> bool:
    author_id = _author_id_from_message(message)
    if author_id == bot_user_id:
        return True
    bot_tag = message.locator('[class*="botTag"], [class*="botText"]').first
    return bot_tag.count() > 0


def login_interactive(auth_state_path: Path, *, headless: bool = False) -> None:
    from playwright.sync_api import sync_playwright

    auth_state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="en-US",
        )
        page = context.new_page()
        page.goto(DISCORD_LOGIN_URL, wait_until="domcontentloaded")
        print(
            "\n1. Complete Discord login in the browser window (2FA if enabled).\n"
            "2. When you see your friends/DMs home screen, return here and press Enter.\n"
        )
        input("Press Enter to save session...")
        context.storage_state(path=str(auth_state_path))
        browser.close()

    print(f"Saved session to {auth_state_path}")


def _open_channel(page: Page, config: DocScreenshotConfig) -> None:
    page.goto(_channel_url(config.guild_id, config.channel_id), wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=60_000)
    _find_message_input(page).wait_for(state="visible", timeout=60_000)


def _send_slash_command(page: Page, slash_command: str) -> None:
    textbox = _find_message_input(page)
    textbox.click()
    textbox.fill("")
    page.keyboard.type(slash_command, delay=30)
    page.keyboard.press("Enter")


def _wait_for_bot_reply(
    page: Page,
    *,
    bot_user_id: str,
    previous_count: int,
    timeout_ms: int,
) -> Locator:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_error = "timed out waiting for bot reply"

    while time.monotonic() < deadline:
        items = _message_items(page)
        count = items.count()
        if count > previous_count:
            for idx in range(count - 1, max(previous_count - 1, 0) - 1, -1):
                message = items.nth(idx)
                if _is_bot_message(message, bot_user_id):
                    message.wait_for(state="visible", timeout=5_000)
                    return message
            last_error = "new messages appeared but none matched the bot user"
        page.wait_for_timeout(400)

    raise RuntimeError(last_error)


def capture_shot(page: Page, config: DocScreenshotConfig, shot: ScreenshotShot) -> Path:
    wait_ms = shot.wait_ms or config.default_wait_ms

    _open_channel(page, config)
    before = _message_items(page).count()
    _send_slash_command(page, shot.slash_command)
    message = _wait_for_bot_reply(
        page,
        bot_user_id=config.bot_user_id,
        previous_count=before,
        timeout_ms=wait_ms,
    )
    page.wait_for_timeout(500)

    shot.output.parent.mkdir(parents=True, exist_ok=True)
    message.screenshot(path=str(shot.output))
    return shot.output


def run_manifest(
    config: DocScreenshotConfig,
    shots: list[ScreenshotShot],
    *,
    auth_state_path: Path,
) -> list[Path]:
    from playwright.sync_api import sync_playwright

    if not auth_state_path.is_file():
        raise SystemExit(
            f"No saved Discord session at {auth_state_path}. "
            "Run: python scripts/generate_doc_screenshots.py login"
        )

    written: list[Path] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=config.headless)
        context = browser.new_context(
            storage_state=str(auth_state_path),
            viewport={"width": config.viewport_width, "height": config.viewport_height},
            locale="en-US",
        )
        page = context.new_page()
        try:
            for shot in shots:
                print(f"Capturing {shot.id}: {shot.slash_command} -> {shot.output}")
                path = capture_shot(page, config, shot)
                print(f"  wrote {path}")
                written.append(path)
        finally:
            browser.close()

    return written

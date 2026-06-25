from __future__ import annotations

import contextlib
import re
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tests.helpers.live_discord.discord_api_sync import (
    _oauth_authorize_query,
    bot_invite_permissions,
)
from tests.helpers.live_discord.timeouts import LiveE2ETimeouts

DEFAULT_TIMEOUTS = LiveE2ETimeouts.from_env(
    playwright_default_ms=30_000,
    playwright_navigation_ms=60_000,
    bootstrap_sec=180,
    token_capture_ms=30_000,
    app_gate_ms=15_000,
    guild_create_ms=90_000,
    oauth_ui_ms=25_000,
    oauth_scroll_ms=60_000,
    open_channel_ms=45_000,
)

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

MESSAGE_INPUT_SELECTORS = (
    'div[role="textbox"][data-slate-editor="true"]',
    'div[data-slate-editor="true"]',
    'div[aria-label^="Message #"]',
    'div[aria-label^="Nachricht #"]',
    '[class*="channelTextArea"] div[role="textbox"]',
    '[class*="textArea"] div[role="textbox"]',
)
MESSAGE_ITEM_SELECTOR = 'li[id^="chat-messages-"]'


def channel_url(guild_id: str, channel_id: str) -> str:
    return f"https://discord.com/channels/{guild_id}/{channel_id}"


def bot_oauth_web_url(
    application_id: str,
    guild_id: str,
    *,
    permissions: str | None = None,
) -> str:
    from tests.helpers.live_discord.discord_api_sync import bot_invite_permissions

    query = _oauth_authorize_query(
        application_id=application_id,
        guild_id=guild_id,
        permissions=permissions or bot_invite_permissions(),
    )
    return f"https://discord.com/oauth2/authorize?{query}"


def _oauth_post_result_ok(result: dict[str, Any]) -> bool:
    from tests.helpers.live_discord.rate_limit import raise_for_rate_limit

    status = int(result.get("status", 0))
    text = str(result.get("text", ""))
    raise_for_rate_limit(status=status, payload=text, action="in-page POST /oauth2/authorize")
    if "captcha" in text.lower():
        return False
    if status in (200, 201, 204, 301, 302, 303, 307, 308):
        return True
    return False


def _discord_client_build_number(page: Page) -> int:
    build = page.evaluate(
        """() => {
            const raw = window.GLOBAL_ENV?.BUILD_NUMBER;
            const parsed = Number(raw);
            return Number.isFinite(parsed) ? parsed : null;
        }"""
    )
    return int(build) if build else 360320


def _authorize_bot_via_token_fetch(
    page: Page,
    *,
    user_token: str,
    application_id: str,
    guild_id: str,
    permissions: str | None = None,
) -> bool:
    permissions = permissions or bot_invite_permissions()
    if "discord.com" not in page.url:
        page.goto("https://discord.com/channels/@me", wait_until="domcontentloaded")
        ensure_discord_web_client(page)
        page.wait_for_timeout(800)

    query = _oauth_authorize_query(
        application_id=application_id,
        guild_id=guild_id,
        permissions=permissions,
    )
    client_build = _discord_client_build_number(page)
    result = page.evaluate(
        """async ({ query, guildId, permissions, userToken, clientBuild }) => {
            const superProps = btoa(JSON.stringify({
                os: "Linux",
                browser: "Chrome",
                device: "",
                system_locale: "en-US",
                browser_user_agent: navigator.userAgent,
                browser_version: "120.0.0.0",
                os_version: "",
                referrer: "",
                referring_domain: "",
                referrer_current: "",
                referring_domain_current: "",
                release_channel: "stable",
                client_build_number: clientBuild,
                client_event_source: null,
            }));
            const res = await fetch(
                `https://discord.com/api/v10/oauth2/authorize?${query}`,
                {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': userToken,
                        'X-Super-Properties': superProps,
                    },
                    body: JSON.stringify({
                        authorize: true,
                        guild_id: guildId,
                        permissions: String(permissions),
                        integration_type: 0,
                    }),
                },
            );
            return { status: res.status, text: await res.text() };
        }""",
        {
            "query": query,
            "guildId": guild_id,
            "permissions": permissions,
            "userToken": user_token.strip(),
            "clientBuild": client_build,
        },
    )
    return _oauth_post_result_ok(result)


_APP_DETECTED_MARKERS = (
    "Discord App Detected",
    "Opening Discord App",
    "Discord-App erkannt",
    "Discord-App wird geöffnet",
)


def _page_shows_app_gate(page: Page) -> bool:
    try:
        body = page.locator("body").inner_text(timeout=2_000)
    except Exception:
        return False
    if any(marker in body for marker in _APP_DETECTED_MARKERS):
        return True
    return "Open App" in body and re.search(r"Continue in Browser|Im Browser", body, re.I) is not None


def _click_continue_in_browser(page: Page) -> bool:
    patterns = (
        r"^Continue in Browser$",
        r"^Continue in browser$",
        r"^Im Browser( fortsetzen| weiter| öffnen)?$",
    )
    for pattern in patterns:
        for role in ("link", "button"):
            loc = page.get_by_role(role, name=re.compile(pattern, re.I))
            if loc.count() > 0:
                loc.first.click(force=True, timeout=10_000)
                page.wait_for_timeout(500)
                return True

    text = page.get_by_text(re.compile(r"Continue in Browser|Im Browser", re.I))
    if text.count() > 0:
        text.first.click(force=True, timeout=10_000)
        page.wait_for_timeout(500)
        return True

    clicked = page.evaluate(
        """() => {
            const match = (el) =>
                el instanceof HTMLElement &&
                /continue in browser|im browser/i.test(el.textContent || "") &&
                el.offsetParent !== null;
            const nodes = document.querySelectorAll("span, a, button, div, p");
            for (const el of nodes) {
                if (!match(el)) continue;
                if (el.textContent.trim().length > 40) continue;
                el.click();
                return true;
            }
            return false;
        }"""
    )
    if clicked:
        page.wait_for_timeout(500)
    return bool(clicked)


def ensure_discord_web_client(
    page: Page,
    *,
    timeout_ms: int = DEFAULT_TIMEOUTS.app_gate_ms,
) -> None:
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        if not _page_shows_app_gate(page):
            return
        if _click_continue_in_browser(page):
            with contextlib.suppress(Exception):
                page.wait_for_load_state("domcontentloaded", timeout=5_000)
            continue
        page.wait_for_timeout(300)
    raise RuntimeError(
        f"Discord desktop-app gate did not clear within {timeout_ms / 1000:.0f}s. "
        "Run once with TANJUN_E2E_HEADLESS=false and click Continue in Browser."
    )


def _oauth_page_ready(page: Page) -> bool:
    try:
        body = page.locator("body").inner_text(timeout=2_000)
    except Exception:
        return False
    if any(marker in body for marker in _APP_DETECTED_MARKERS):
        return False
    return bool(re.search(r"wants to access|Authorize|Authorisieren|Keep Scrolling", body, re.I))


def _dismiss_slash_overlays(page: Page) -> None:
    for _ in range(3):
        with contextlib.suppress(Exception):
            page.keyboard.press("Escape")
        page.wait_for_timeout(200)


def find_message_input(page: Page) -> Locator:
    _dismiss_slash_overlays(page)
    for selector in MESSAGE_INPUT_SELECTORS:
        loc = page.locator(selector).first
        if loc.count() > 0:
            return loc
    raise RuntimeError("Discord message input not found; update MESSAGE_INPUT_SELECTORS")


def wait_for_message_input(
    page: Page,
    *,
    timeout_ms: int = 45_000,
) -> Locator:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            loc = find_message_input(page)
            loc.wait_for(state="visible", timeout=2_000)
            return loc
        except Exception as exc:
            last_error = exc
            page.wait_for_timeout(500)
    if last_error is not None:
        raise RuntimeError("Discord message input not found; update MESSAGE_INPUT_SELECTORS") from last_error
    raise RuntimeError("Discord message input not found; update MESSAGE_INPUT_SELECTORS")


def _dismiss_continue_in_browser(page: Page) -> None:
    if _click_continue_in_browser(page):
        return
    for pattern in (
        r"Continue to Discord",
        r"Weiter zu Discord",
        r"Not now",
        r"Nicht jetzt",
        r"Dismiss",
    ):
        button = page.get_by_role("button", name=re.compile(pattern, re.I))
        if button.count() > 0:
            button.first.click(timeout=10_000)
            page.wait_for_timeout(600)
            return


def _oauth_scroll_container_handle(page: Page) -> object | None:
    return page.evaluate(
        """() => {
            const keep = [...document.querySelectorAll("button")].find((btn) =>
                /keep scrolling|weiter scrollen|scroll down/i.test(btn.textContent || "")
            );
            let node = keep?.parentElement ?? null;
            while (node) {
                if (node.scrollHeight > node.clientHeight + 8) {
                    return node;
                }
                node = node.parentElement;
            }
            const candidates = [
                ...document.querySelectorAll(
                    '[class*="authorize"], [class*="modal"], [role="dialog"], form, main'
                ),
            ];
            for (const el of candidates) {
                if (el.scrollHeight > el.clientHeight + 8) {
                    return el;
                }
            }
            return document.scrollingElement || document.body;
        }"""
    )


def _scroll_oauth_permissions_panel(page: Page) -> None:
    handle = _oauth_scroll_container_handle(page)
    if handle is not None:
        page.evaluate(
            """(el) => {
                const step = Math.max(el.clientHeight - 40, 120);
                for (let i = 0; i < 24; i += 1) {
                    el.scrollTop = Math.min(el.scrollTop + step, el.scrollHeight);
                    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 4) {
                        break;
                    }
                }
                el.scrollTop = el.scrollHeight;
            }""",
            handle,
        )
    page.keyboard.press("PageDown")
    page.keyboard.press("End")
    page.mouse.wheel(0, 1200)


def _oauth_authorize_button(page: Page) -> Locator:
    return page.get_by_role(
        "button",
        name=re.compile(r"^(Authorize|Authorisieren|Autorisieren)$", re.I),
    )


def _scroll_oauth_until_authorize(page: Page, *, timeout_ms: int) -> Locator:
    deadline = time.monotonic() + (timeout_ms / 1000)
    keep_clicks = 0
    while time.monotonic() < deadline:
        _dismiss_continue_in_browser(page)

        authorize = _oauth_authorize_button(page)
        if authorize.count() > 0:
            with contextlib.suppress(Exception):
                authorize.first.wait_for(state="visible", timeout=2_000)
            if authorize.first.is_enabled():
                return authorize.first

        keep_scrolling = page.get_by_role(
            "button",
            name=re.compile(r"Keep Scrolling|Weiter scrollen|Scroll down", re.I),
        )
        _scroll_oauth_permissions_panel(page)
        if keep_scrolling.count() > 0:
            keep = keep_scrolling.first
            box = keep.bounding_box()
            if box is not None:
                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                page.mouse.wheel(0, 600)
            if keep.is_enabled():
                keep.click(timeout=5_000)
                keep_clicks += 1
            elif keep_clicks < 3:
                with contextlib.suppress(Exception):
                    keep.click(force=True, timeout=2_000)
                    keep_clicks += 1
            page.wait_for_timeout(500)
            continue

        with contextlib.suppress(Exception):
            page.wait_for_function(
                """() => {
                    const btn = [...document.querySelectorAll("button")].find((el) =>
                        /^(authorize|authorisieren|autorisieren)$/i.test(
                            (el.textContent || "").trim()
                        )
                    );
                    return btn && !btn.disabled;
                }""",
                timeout=1_500,
            )
            authorize = _oauth_authorize_button(page)
            if authorize.count() > 0 and authorize.first.is_enabled():
                return authorize.first

        page.wait_for_timeout(400)

    raise RuntimeError(
        f"Discord OAuth Authorize button did not appear within {timeout_ms / 1000:.0f}s. "
        "Set TANJUN_E2E_OAUTH_HEADLESS=false (or unset DISPLAY) and complete scroll in the "
        "Chromium window, or reuse a guild where the bot is already invited."
    )


def _complete_oauth_authorize_ui(
    oauth_page: Page,
    *,
    timeouts: LiveE2ETimeouts,
    oauth_headless: bool,
) -> None:
    try:
        authorize = _scroll_oauth_until_authorize(
            oauth_page,
            timeout_ms=timeouts.oauth_scroll_ms,
        )
        authorize.click(timeout=timeouts.playwright_default_ms)
    except RuntimeError:
        if oauth_headless:
            raise
        print(
            "\n[live e2e] OAuth scroll automation did not finish — "
            "complete Keep Scrolling and Authorize in the Chromium window.\n",
            flush=True,
        )
    oauth_page.wait_for_url(
        re.compile(r"discord\.com/channels"),
        timeout=timeouts.playwright_navigation_ms,
    )


def _block_desktop_app_handoff(page: Page) -> None:
    def _abort_external(route) -> None:
        url = route.request.url
        if url.startswith(("discord://", "discordapp://", "intent://")):
            route.abort()
            return
        route.continue_()

    page.route("**/*", _abort_external)


def _wait_for_oauth_content(page: Page, *, timeout_ms: int) -> None:
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        if _oauth_page_ready(page) or _page_shows_app_gate(page):
            return
        with contextlib.suppress(Exception):
            if len(page.locator("body").inner_text(timeout=1_000).strip()) > 20:
                return
        page.wait_for_timeout(300)
    raise RuntimeError(f"OAuth page did not load content within {timeout_ms / 1000:.0f}s.")


def _authorize_bot_via_fresh_oauth_context(
    browser: object,
    *,
    auth_state_path: str,
    application_id: str,
    guild_id: str,
    permissions: str,
    oauth_headless: bool,
    timeouts: LiveE2ETimeouts,
) -> None:
    from playwright.sync_api import Browser

    if not isinstance(browser, Browser):
        raise TypeError("browser must be a Playwright Browser")

    from tests.helpers.live_discord.chromium_launch import CHROMIUM_ARGS

    oauth_url = bot_oauth_web_url(application_id, guild_id, permissions=permissions)
    oauth_browser = browser.browser_type.launch(
        headless=oauth_headless,
        args=list(CHROMIUM_ARGS),
    )
    oauth_context = oauth_browser.new_context(
        storage_state=auth_state_path,
        locale="en-US",
        viewport={"width": 1280, "height": 900},
    )
    oauth_context.set_default_timeout(timeouts.playwright_default_ms)
    oauth_context.set_default_navigation_timeout(timeouts.playwright_navigation_ms)
    oauth_page = oauth_context.new_page()
    _block_desktop_app_handoff(oauth_page)
    try:
        oauth_page.goto(
            oauth_url,
            wait_until="domcontentloaded",
            timeout=timeouts.playwright_navigation_ms,
        )
        _wait_for_oauth_content(oauth_page, timeout_ms=timeouts.oauth_ui_ms)
        deadline = time.monotonic() + (timeouts.oauth_ui_ms / 1000)
        while time.monotonic() < deadline:
            if _oauth_page_ready(oauth_page):
                break
            with contextlib.suppress(RuntimeError):
                ensure_discord_web_client(oauth_page, timeout_ms=3_000)
            oauth_page.wait_for_timeout(400)
        else:
            raise RuntimeError(
                f"OAuth did not reach the Authorize form within {timeouts.oauth_ui_ms / 1000:.0f}s. "
                "In the opened Chromium window, click Continue in Browser if shown, then scroll and Authorize."
            )
        _complete_oauth_authorize_ui(
            oauth_page,
            timeouts=timeouts,
            oauth_headless=oauth_headless,
        )
    finally:
        oauth_page.close()
        oauth_context.close()
        oauth_browser.close()


def authorize_bot_to_guild(
    page: Page,
    *,
    browser: object,
    auth_state_path: str,
    user_token: str,
    bot_token: str,
    bot_user_id: str,
    application_id: str,
    guild_id: str,
    permissions: str | None = None,
    oauth_headless: bool = True,
    timeouts: LiveE2ETimeouts = DEFAULT_TIMEOUTS,
) -> None:
    from tests.helpers.live_discord.discord_api_sync import bot_invite_permissions

    perms = permissions or bot_invite_permissions()
    from tests.helpers.live_discord.discord_api_sync import authorize_bot_to_guild as sync_authorize
    from tests.helpers.live_discord.discord_api_sync import bot_is_guild_member
    from tests.helpers.live_discord.rate_limit import DiscordRateLimitedError, is_captcha_payload

    if bot_is_guild_member(bot_token, guild_id, bot_user_id):
        return

    try:
        sync_authorize(
            user_token,
            application_id=application_id,
            guild_id=guild_id,
            permissions=perms,
        )
        return
    except DiscordRateLimitedError:
        raise
    except RuntimeError as exc:
        if not is_captcha_payload(str(exc)):
            raise

    if _authorize_bot_via_token_fetch(
        page,
        user_token=user_token,
        application_id=application_id,
        guild_id=guild_id,
        permissions=perms,
    ):
        return

    _authorize_bot_via_fresh_oauth_context(
        browser,
        auth_state_path=auth_state_path,
        application_id=application_id,
        guild_id=guild_id,
        permissions=perms,
        oauth_headless=oauth_headless,
        timeouts=timeouts,
    )


def _click_first_matching(page: Page, *, role: str | None, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        loc = page.get_by_role(role, name=re.compile(pattern, re.I)) if role else page.get_by_text(re.compile(pattern, re.I))
        if loc.count() > 0:
            loc.first.click(timeout=30_000)
            page.wait_for_timeout(400)
            return True
    return False


def create_guild_via_ui(
    page: Page,
    guild_name: str,
    *,
    timeouts: LiveE2ETimeouts = DEFAULT_TIMEOUTS,
) -> tuple[str, str]:
    page.goto(
        "https://discord.com/channels/@me",
        wait_until="domcontentloaded",
        timeout=timeouts.playwright_navigation_ms,
    )
    ensure_discord_web_client(page, timeout_ms=timeouts.app_gate_ms)
    page.wait_for_timeout(1500)

    if not _click_first_matching(
        page,
        role="button",
        patterns=(
            r"Add a Server",
            r"Server hinzufügen",
            r"Add a server",
        ),
    ):
        add_server = page.locator(
            '[aria-label="Add a Server"], [aria-label="Server hinzufügen"], [data-list-item-id="guild-create"]'
        ).first
        add_server.click(timeout=30_000)
        page.wait_for_timeout(500)

    _click_first_matching(
        page,
        role=None,
        patterns=(
            r"Create My Own",
            r"Eigenen Server erstellen",
            r"Create your own",
            r"Erstelle deinen",
        ),
    )
    _click_first_matching(
        page,
        role=None,
        patterns=(
            r"For me and my friends",
            r"Für mich und meine Freunde",
            r"For a club or community",
            r"Für einen Verein",
        ),
    )

    name_input = page.locator('input[type="text"]').last
    name_input.wait_for(state="visible", timeout=30_000)
    name_input.fill(guild_name)

    if not _click_first_matching(
        page,
        role="button",
        patterns=(r"^Create$", r"^Erstellen$", r"^Done$", r"^Fertig$"),
    ):
        page.keyboard.press("Enter")

    page.wait_for_url(
        re.compile(r"discord\.com/channels/(\d+)/(\d+)"),
        timeout=timeouts.guild_create_ms,
    )
    match = re.search(r"/channels/(\d+)/(\d+)", page.url)
    if not match:
        raise RuntimeError(f"Could not parse guild/channel from URL: {page.url}")
    return match.group(1), match.group(2)


def open_channel(
    page: Page,
    guild_id: str,
    channel_id: str,
    *,
    timeouts: LiveE2ETimeouts = DEFAULT_TIMEOUTS,
) -> None:
    target = channel_url(guild_id, channel_id)
    if not page.url.startswith(target):
        page.goto(
            target,
            wait_until="domcontentloaded",
            timeout=timeouts.playwright_navigation_ms,
        )
    ensure_discord_web_client(page, timeout_ms=timeouts.app_gate_ms)
    with contextlib.suppress(Exception):
        page.wait_for_load_state("networkidle", timeout=10_000)
    wait_for_message_input(page, timeout_ms=timeouts.open_channel_ms)


def _message_items(page: Page) -> Locator:
    return page.locator(MESSAGE_ITEM_SELECTOR)


def _is_bot_message(message: Locator, bot_user_id: str) -> bool:
    for selector in ('a[href*="/users/"]',):
        link = message.locator(selector).first
        if link.count() == 0:
            continue
        href = link.get_attribute("href") or ""
        match = re.search(r"/users/(\d+)", href)
        if match and match.group(1) == bot_user_id:
            return True
    bot_tag = message.locator('[class*="botTag"], [class*="botText"]').first
    return bot_tag.count() > 0


def wait_for_bot_message_locator(
    page: Page,
    *,
    bot_user_id: str,
    previous_count: int,
    timeout_ms: int,
) -> Locator:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_error = "timed out waiting for bot message in channel"
    while time.monotonic() < deadline:
        items = _message_items(page)
        count = items.count()
        if count > previous_count:
            for idx in range(count - 1, max(previous_count - 1, 0) - 1, -1):
                message = items.nth(idx)
                if _is_bot_message(message, bot_user_id):
                    message.wait_for(state="visible", timeout=5_000)
                    return message
            last_error = "new messages appeared but none from the bot"
        page.wait_for_timeout(400)
    raise RuntimeError(last_error)


_SLASH_OPTION_SELECTORS = (
    '[class*="autocompleteRow"]',
    '[class*="commandSuggestion"]',
    '[class*="applicationCommand"]',
    '[class*="option-"]',
    '[data-list-item-id*="commands"]',
    '[role="option"]',
)


def _slash_option_locator(page: Page, needles: str | tuple[str, ...]) -> Locator:
    if isinstance(needles, str):
        needles = (needles,)
    combined = page.locator(", ".join(_SLASH_OPTION_SELECTORS))
    for needle in needles:
        if not needle:
            continue
        pattern = re.compile(re.escape(needle), re.I)
        match = combined.filter(has_text=pattern).first
        if match.count() > 0:
            return match
    return combined.filter(has_text=re.compile("$^")).first


def _slash_autocomplete_visible(page: Page, needles: str | tuple[str, ...]) -> bool:
    if isinstance(needles, str):
        needles = (needles,)
    for needle in needles:
        if needle and _slash_option_locator(page, needle).count() > 0:
            return True
    return False


def _any_slash_autocomplete_visible(page: Page) -> bool:
    return page.locator(", ".join(_SLASH_OPTION_SELECTORS)).count() > 0


def _clear_message_composer(page: Page, textbox: Locator) -> None:
    textbox.click()
    with contextlib.suppress(Exception):
        textbox.fill("")
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.wait_for_timeout(200)


def _wait_pick_slash_option(
    page: Page,
    needles: str | tuple[str, ...],
    *,
    timeout_ms: int = 20_000,
    allow_keyboard_fallback: bool = False,
) -> None:
    if isinstance(needles, str):
        needles = (needles,)
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        option = _slash_option_locator(page, needles)
        if option.count() > 0:
            with contextlib.suppress(Exception):
                option.click(timeout=5_000)
                page.wait_for_timeout(400)
                return
            with contextlib.suppress(Exception):
                option.focus()
                page.keyboard.press("Tab")
                page.wait_for_timeout(400)
                return
        if allow_keyboard_fallback and _any_slash_autocomplete_visible(page):
            rows = page.locator(", ".join(_SLASH_OPTION_SELECTORS))
            if rows.count() == 1:
                with contextlib.suppress(Exception):
                    page.keyboard.press("ArrowDown")
                    page.wait_for_timeout(200)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(400)
                    return
        page.wait_for_timeout(250)
    raise RuntimeError(
        f"Could not select slash option {needles!r} from autocomplete. "
        "The test bot must be online with synced /funcmd_name (shown as 'fun' in Discord). "
        "Typing Enter without a match sends plain text."
    )


def _type_slash_command_query(page: Page, textbox: Locator, query: str) -> None:
    _clear_message_composer(page, textbox)
    page.keyboard.type(f"/{query}", delay=35)
    page.wait_for_timeout(1_200)


def _pick_slash_command_query(
    page: Page,
    textbox: Locator,
    *,
    type_queries: tuple[str, ...],
    pick_needles: tuple[str, ...],
    timeout_ms: int,
) -> None:
    last_error: RuntimeError | None = None
    per_query_timeout = max(8_000, timeout_ms // max(len(type_queries), 1))
    for query in type_queries:
        _type_slash_command_query(page, textbox, query)
        try:
            _wait_pick_slash_option(page, pick_needles, timeout_ms=per_query_timeout)
            return
        except RuntimeError as exc:
            last_error = exc
            with contextlib.suppress(Exception):
                page.keyboard.press("Escape")
            page.wait_for_timeout(300)
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Could not select slash command from queries {type_queries!r}")


def _pick_member_mention(page: Page, display_name: str) -> None:
    fragment = display_name[:32].strip()
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        option = page.locator('[class*="autocompleteRow"]').filter(has_text=fragment).first
        if option.count() > 0:
            option.click(timeout=5_000)
            page.wait_for_timeout(300)
            return
        page.wait_for_timeout(250)
    page.keyboard.press("Enter")
    page.wait_for_timeout(300)


def _commit_fun_subcommand(page: Page, textbox: Locator, action: str) -> None:
    from tests.helpers.fun_matrix import fun_full_slash_type_queries, fun_subcommand_slash_needles

    sub_needles = fun_subcommand_slash_needles(action)
    action_pattern = re.compile(re.escape(action), re.I)
    last_error: RuntimeError | None = None
    for query in fun_full_slash_type_queries(action):
        _type_slash_command_query(page, textbox, query)
        row = (
            page.locator('[class*="autocompleteRow"]')
            .filter(has_text=action_pattern)
            .filter(has_text=re.compile(r"fun|funcmd", re.I))
            .first
        )
        if row.count() > 0:
            row.click(timeout=5_000)
            page.wait_for_timeout(700)
            return
        try:
            _wait_pick_slash_option(page, sub_needles, timeout_ms=8_000)
            page.wait_for_timeout(400)
            return
        except RuntimeError as exc:
            last_error = exc
            with contextlib.suppress(Exception):
                page.keyboard.press("Escape")
            page.wait_for_timeout(300)
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Could not commit /fun {action} slash command")


def _fill_user_parameter(page: Page, target_display_name: str) -> None:
    from tests.helpers.fun_matrix import fun_member_param_labels

    for label in fun_member_param_labels():
        pill = page.locator('[class*="optionPill"], [class*="optionName"]').filter(
            has_text=re.compile(rf"^{re.escape(label)}$", re.I)
        )
        if pill.count() > 0:
            pill.first.click(timeout=3_000)
            page.wait_for_timeout(300)
            break
    else:
        page.keyboard.press("Tab")
        page.wait_for_timeout(400)

    page.keyboard.type("@" + target_display_name[:32], delay=25)
    page.wait_for_timeout(900)
    _pick_member_mention(page, target_display_name)


def _fill_message_parameter(page: Page, message: str) -> None:
    for label in ("message", "Message", "Nachricht"):
        pill = page.locator('[class*="optionPill"], [class*="optionName"]').filter(
            has_text=re.compile(rf"^{re.escape(label)}$", re.I)
        )
        if pill.count() > 0:
            pill.first.click(timeout=3_000)
            page.wait_for_timeout(250)
            break
    else:
        page.keyboard.press("Tab")
        page.wait_for_timeout(250)
    page.keyboard.type(message, delay=15)


def wait_for_fun_slash_commands(
    page: Page,
    *,
    group_name: str,
    sample_subcommand: str,
    timeout_ms: int,
    group_needles: tuple[str, ...] | None = None,
    subcommand_needles: tuple[str, ...] | None = None,
    type_queries: tuple[str, ...] | None = None,
) -> None:
    from tests.helpers.fun_matrix import (
        fun_full_slash_type_queries,
        fun_group_slash_needles,
        fun_subcommand_slash_needles,
    )

    group_labels = group_needles or fun_group_slash_needles()
    sample_action = sample_subcommand.removeprefix("fun_").removesuffix("_name")
    sub_labels = subcommand_needles or fun_subcommand_slash_needles(sample_action)
    queries = type_queries or fun_full_slash_type_queries(sample_action)
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_error = "slash autocomplete did not appear"
    textbox = wait_for_message_input(page, timeout_ms=min(timeout_ms, 45_000))
    while time.monotonic() < deadline:
        for query in queries:
            _type_slash_command_query(page, textbox, query)
            if _slash_autocomplete_visible(page, group_labels) or _slash_autocomplete_visible(page, sub_labels):
                page.keyboard.press("Escape")
                page.wait_for_timeout(200)
                return
            last_error = f"no autocomplete for /{query} ({group_labels!r}) (url={page.url[:80]})"
            page.keyboard.press("Escape")
            page.wait_for_timeout(800)
        page.wait_for_timeout(700)
    raise RuntimeError(
        f"{last_error} within {timeout_ms / 1000:.0f}s. "
        "Start the test bot and wait for command sync, or set TANJUN_E2E_SKIP_COMMAND_SYNC=0."
    )


def invoke_fun_slash(
    page: Page,
    *,
    group_name: str,
    subcommand_name: str,
    target_display_name: str,
    optional_message: str | None,
    bot_user_id: str,
    wait_ms: int,
    group_needles: tuple[str, ...] | None = None,
    subcommand_needles: tuple[str, ...] | None = None,
) -> None:
    action = subcommand_name.removeprefix("fun_").removesuffix("_name")
    textbox = wait_for_message_input(page)

    _commit_fun_subcommand(page, textbox, action)
    _fill_user_parameter(page, target_display_name)

    if optional_message is not None:
        _fill_message_parameter(page, optional_message)

    page.keyboard.press("Enter")
    page.wait_for_timeout(600)


def save_debug_screenshot(page: Page, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), full_page=True)

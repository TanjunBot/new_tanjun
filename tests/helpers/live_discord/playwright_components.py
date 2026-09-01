from __future__ import annotations

from typing import Any


async def click_first_button_on_message(page: Any, *, message_id: str) -> None:
    if page is None:
        return
    selector = f'[data-list-item-id="chat-messages___chat-messages-{message_id}"] button'
    button = page.locator(selector).first
    if await button.count() == 0:
        button = page.locator("button").first
    if await button.count() > 0:
        await button.click()


async def click_wizard_next(page: Any) -> None:
    if page is None:
        return
    for label in ("Next", "Weiter", "Continue"):
        button = page.get_by_role("button", name=label)
        if await button.count() > 0:
            await button.first.click()
            return
    await click_first_button_on_message(page, message_id="")


async def click_wizard_finish(page: Any) -> None:
    if page is None:
        return
    for label in ("Finish", "Done", "Fertig", "Complete", "Save"):
        button = page.get_by_role("button", name=label)
        if await button.count() > 0:
            await button.first.click()
            return
    await click_wizard_next(page)


async def run_wizard_flow(page: Any, *, steps: int = 3) -> None:
    if page is None:
        return
    for _ in range(steps):
        await click_wizard_next(page)
    await click_wizard_finish(page)


async def click_game_button(page: Any, *, label: str | None = None) -> None:
    if page is None:
        return
    if label:
        button = page.get_by_role("button", name=label)
        if await button.count() > 0:
            await button.first.click()
            return
    await click_first_button_on_message(page, message_id="")

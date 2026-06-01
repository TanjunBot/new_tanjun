from __future__ import annotations

import json
from pathlib import Path

from diagnostics.models import CheckOutcome
from localizer import tanjunLocalizer

_LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"

_SAMPLE_KEYS = (
    "commands.admin.administration.test_bot.starting",
    "commands.admin.administration.test_bot.all_completed",
    "commands.admin.administration.test_bot.error",
    "commands.fun.hug.title",
    "commands.games.akinator.description",
    "commands.channel.dynamicslowmode.success.title",
    "commands.admin.ban.error.description",
)


def check_locale_files() -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []
    paths = sorted(_LOCALES_DIR.glob("*.json"))
    if not paths:
        return [CheckOutcome("locale.files", False, "No locale files under locales/")]

    for path in paths:
        check_id = f"locale.file.{path.stem}"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            outcomes.append(CheckOutcome(check_id, False, str(exc)))
            continue
        if not isinstance(data, list):
            outcomes.append(CheckOutcome(check_id, False, "Expected JSON array of translation entries"))
            continue
        ids = [str(entry.get("identifier", "")) for entry in data if isinstance(entry, dict)]
        empty = [i for i in ids if not i]
        if empty:
            outcomes.append(CheckOutcome(check_id, False, f"{len(empty)} entries missing identifier"))
            continue
        outcomes.append(CheckOutcome(check_id, True, f"{len(ids)} entries"))

    return outcomes


def check_localizer_samples(locale: str = "en") -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []
    for key in _SAMPLE_KEYS:
        check_id = f"locale.sample.{key.rsplit('.', 1)[-1]}"
        try:
            value = tanjunLocalizer.localize(locale, key)
        except Exception as exc:
            outcomes.append(CheckOutcome(check_id, False, str(exc)))
            continue
        if not value or value == "err: no translation found.":
            outcomes.append(CheckOutcome(check_id, False, f"Missing translation for {key!r}"))
        else:
            outcomes.append(CheckOutcome(check_id, True, "OK"))
    return outcomes

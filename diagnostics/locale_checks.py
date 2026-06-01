from __future__ import annotations

import json
from pathlib import Path

from diagnostics.models import CheckOutcome
from locale_keys import locale

_LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"

_SAMPLE_LOOKUPS: tuple[tuple[str, object], ...] = (
    ("starting", locale.commands.admin.administration.test_bot.starting),
    ("all_completed", locale.commands.admin.administration.test_bot.all_completed),
    ("error", locale.commands.admin.administration.test_bot.error),
    ("hug_title", locale.commands.fun.hug.title),
    ("akinator_description", locale.commands.games.akinator.description),
    ("dynamicslowmode_success", locale.commands.channel.dynamicslowmode.success.title),
    ("ban_error", locale.commands.admin.ban.error.title),
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


def check_localizer_samples(loc: str = "en") -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []
    for check_id_suffix, localized in _SAMPLE_LOOKUPS:
        check_id = f"locale.sample.{check_id_suffix}"
        try:
            value = localized(loc)
        except Exception as exc:
            outcomes.append(CheckOutcome(check_id, False, str(exc)))
            continue
        if not value or value == "err: no translation found.":
            outcomes.append(CheckOutcome(check_id, False, f"Missing translation for {check_id_suffix!r}"))
        else:
            outcomes.append(CheckOutcome(check_id, True, "OK"))
    return outcomes

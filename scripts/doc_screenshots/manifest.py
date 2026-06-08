from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ScreenshotShot:
    id: str
    slash_command: str
    output: Path
    wait_ms: int | None = None
    description: str = ""


@dataclass(frozen=True)
class ScreenshotManifest:
    shots: list[ScreenshotShot]
    default_wait_ms: int | None = None


def _resolve_output(path: str) -> Path:
    out = Path(path)
    if out.is_absolute():
        return out
    return (ROOT / out).resolve()


def load_manifest(path: Path) -> ScreenshotManifest:
    if not path.is_file():
        raise SystemExit(f"Manifest not found: {path}")

    raw: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    default_wait_ms = raw.get("default_wait_ms")

    shots: list[ScreenshotShot] = []
    for entry in raw.get("shots", []):
        if not isinstance(entry, dict):
            continue
        shot_id = str(entry.get("id", "")).strip()
        slash = str(entry.get("slash_command", "")).strip()
        output = str(entry.get("output", "")).strip()
        if not shot_id or not slash or not output:
            raise SystemExit(
                f"Invalid manifest entry (need id, slash_command, output): {entry!r}"
            )
        wait_ms = entry.get("wait_ms")
        shots.append(
            ScreenshotShot(
                id=shot_id,
                slash_command=slash if slash.startswith("/") else f"/{slash}",
                output=_resolve_output(output),
                wait_ms=int(wait_ms) if wait_ms is not None else None,
                description=str(entry.get("description", "")),
            )
        )

    if not shots:
        raise SystemExit(f"No shots defined in manifest: {path}")

    return ScreenshotManifest(shots=shots, default_wait_ms=default_wait_ms)

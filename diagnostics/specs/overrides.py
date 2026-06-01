from __future__ import annotations

from typing import Any

SPEC_SKIPS: dict[str, str] = {}

SPEC_OVERRIDES: dict[str, dict[str, Any] | Any] = {}

SPEC_PATCH_TARGETS: dict[str, tuple[str, ...]] = {}

SPEC_CUSTOM_ASSERTIONS: dict[str, Any] = {}

#!/usr/bin/env python3
"""Entry point for Playwright doc screenshots. See docs/dev/doc_screenshots.md."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from doc_screenshots.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

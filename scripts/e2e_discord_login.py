#!/usr/bin/env python3
"""Save Discord browser session for live E2E tests (no guild/channel env required)."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from doc_screenshots.config import load_login_config
from doc_screenshots.playwright_runner import login_interactive

if __name__ == "__main__":
    auth = load_login_config()
    login_interactive(auth.auth_state_path, headless=False)

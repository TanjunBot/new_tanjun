"""Docker health check for Tanjun bot.

Runs in a separate process from main.py, so it cannot use the bot's
in-memory DB pool. Startup checks in main.py already validate the DB
before login; here we only verify on_ready() has run (bot_ready file).
"""

import os
import sys
import tempfile
from pathlib import Path

READY_FILE = Path(os.path.join(tempfile.gettempdir(), "bot_ready"))


def check_health() -> bool:
    return READY_FILE.is_file()


def main() -> None:
    sys.exit(0 if check_health() else 1)


if __name__ == "__main__":
    main()

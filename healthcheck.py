"""Docker health check for Tanjun bot.

Verifies the bot process is alive and has connected to Discord
by checking for the ready flag file written by on_ready().
"""

import os
import sys
import tempfile
from pathlib import Path

READY_FILE = Path(os.path.join(tempfile.gettempdir(), "bot_ready"))


def main() -> None:
    if READY_FILE.exists():
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()

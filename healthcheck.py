"""Docker health check for Tanjun bot.

Runs in a separate process from main.py. Checks the on_ready marker file,
startup marker while migrations or Discord connect are in progress, and as a
fallback the Prometheus /health endpoint once the metrics server is up.
"""

import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

READY_FILE = Path(os.environ.get("BOT_READY_FILE", "/usr/local/app/.bot_ready"))
STARTUP_FILE = Path(os.environ.get("BOT_STARTUP_FILE", "/usr/local/app/.bot_startup"))
METRICS_PORT = int(os.environ.get("METRICS_PORT", "8001"))


def check_ready_file() -> bool:
    return READY_FILE.is_file()


def check_startup_in_progress() -> bool:
    return STARTUP_FILE.is_file()


def check_metrics_health() -> bool:
    url = f"http://127.0.0.1:{METRICS_PORT}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return bool(response.status == 200)
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def check_health() -> bool:
    return check_ready_file() or check_startup_in_progress() or check_metrics_health()


def main() -> None:
    sys.exit(0 if check_health() else 1)


if __name__ == "__main__":
    main()

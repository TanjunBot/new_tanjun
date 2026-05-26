"""Docker health check for Tanjun bot.

Verifies the bot process is alive, has connected to Discord
by checking for the ready flag file written by on_ready(),
and that the database connection pool is responsive.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

READY_FILE = Path(os.path.join(tempfile.gettempdir(), "bot_ready"))


async def check_health() -> bool:
    """Run all health checks and return True only if all pass."""
    # Check 1: Bot has fired on_ready
    if not READY_FILE.exists():
        return False

    # Check 2: Database pool is responsive
    try:
        from api import check_pool_health

        return await check_pool_health()
    except Exception:
        return False


def main() -> None:
    result = asyncio.run(check_health())
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

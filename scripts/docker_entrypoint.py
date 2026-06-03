#!/usr/bin/env python3
"""Container entrypoint: wait for MySQL, apply Alembic migrations, start the bot."""

from __future__ import annotations

import logging
import os
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_DB_WAIT_ATTEMPTS = int(os.environ.get("TANJUN_DB_WAIT_ATTEMPTS", "60"))
_DB_WAIT_DELAY_SEC = float(os.environ.get("TANJUN_DB_WAIT_DELAY_SEC", "2"))


def _wait_for_database() -> None:
    from sqlalchemy import create_engine, text

    from utils.db_migration import get_database_url

    url = get_database_url()
    engine = create_engine(url, pool_pre_ping=True)
    last_error: Exception | None = None

    for attempt in range(1, _DB_WAIT_ATTEMPTS + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection ready (attempt %s)", attempt)
            return
        except Exception as exc:
            last_error = exc
            logger.info(
                "Waiting for database (%s/%s): %s",
                attempt,
                _DB_WAIT_ATTEMPTS,
                exc,
            )
            time.sleep(_DB_WAIT_DELAY_SEC)

    raise RuntimeError("Database not reachable before startup timeout") from last_error


def main() -> None:
    os.chdir(os.environ.get("TANJUN_APP_ROOT", "/usr/local/app"))

    logger.info("Checking database connectivity")
    _wait_for_database()

    from utils.db_migration import ensure_database_schema

    ensure_database_schema()

    logger.info("Starting Tanjun bot")
    os.execvp(sys.executable, [sys.executable, "main.py", *sys.argv[1:]])


if __name__ == "__main__":
    main()

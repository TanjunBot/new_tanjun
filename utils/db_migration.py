from __future__ import annotations

import logging
import os
from urllib.parse import quote_plus

from alembic.config import Config

logger = logging.getLogger(__name__)


def _first_env(*keys: str, default: str | None = None) -> str | None:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return default


def get_database_url() -> str:
    """Build a SQLAlchemy URL for Alembic (sync PyMySQL driver)."""
    host = _first_env("TANJUN_TEST_DB_HOST", "database_ip", "DATABASE_IP", "MARIADB_HOST", "MYSQL_HOST")
    port = _first_env("TANJUN_TEST_DB_PORT", "database_port", "DATABASE_PORT", "MARIADB_PORT", "MYSQL_PORT", default="3306")
    user = _first_env("TANJUN_TEST_DB_USER", "database_user", "DATABASE_USER", "MARIADB_USER", "MYSQL_USER")
    password = _first_env(
        "TANJUN_TEST_DB_PASSWORD",
        "database_password",
        "DATABASE_PASSWORD",
        "MARIADB_PASSWORD",
        "MYSQL_PASSWORD",
    )
    database = _first_env(
        "TANJUN_TEST_DB_NAME",
        "database_schema",
        "DATABASE_SCHEMA",
        "MARIADB_DATABASE",
        "MYSQL_DATABASE",
    )

    if host is None or user is None or password is None or database is None:
        try:
            from config import settings

            host = host or settings.database_ip
            port = str(port or settings.database_port)
            user = user or settings.database_user
            password = password if password is not None else settings.database_password.get_secret_value()
            database = database or settings.database_schema
        except Exception:
            pass

    if host is None or user is None or password is None or database is None:
        raise RuntimeError(
            "Database credentials missing for migrations. Set database_* env vars or TANJUN_TEST_DB_*."
        )

    safe_user = quote_plus(str(user))
    safe_password = quote_plus(str(password))
    return f"mysql+pymysql://{safe_user}:{safe_password}@{host}:{port}/{database}"


def _alembic_config() -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", get_database_url())
    return cfg


def _revision_state(cfg: Config) -> tuple[str | None, str | None]:
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory
    from sqlalchemy import create_engine

    script = ScriptDirectory.from_config(cfg)
    head = script.get_current_head()
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        try:
            current = context.get_current_revision()
        except Exception:
            current = None
    return current, head


def ensure_database_schema() -> None:
    """Bring the database to the latest schema using Alembic.

    - Empty or outdated schema: ``alembic upgrade head``
    - Schema already matches code but ``alembic_version`` is missing: ``alembic stamp head``
    - Already at head with matching schema: no-op
    """
    from alembic import command
    from sqlalchemy import create_engine

    from utils.schema_conformance import schema_has_drift

    cfg = _alembic_config()
    current, head = _revision_state(cfg)

    if head is None:
        raise RuntimeError("No Alembic head revision found")

    engine = create_engine(get_database_url(), pool_pre_ping=True)

    with engine.connect() as connection:
        drift = schema_has_drift(connection)

    if current == head and not drift:
        logger.info("Database schema is current (Alembic revision %s)", head)
        return

    if current == head and drift:
        raise RuntimeError(
            "Schema drift detected at Alembic head (%s). Add a repair migration instead of auto-repair:\n"
            % len(drift)
            + "\n".join(drift)
        )

    if current is None and not drift:
        logger.info(
            "Database schema matches head but alembic_version is unset; stamping revision %s",
            head,
        )
        command.stamp(cfg, "head")
        return

    logger.info(
        "Applying Alembic migrations (current=%s, head=%s, drift_items=%s)",
        current,
        head,
        len(drift),
    )
    command.upgrade(cfg, "head")

    with engine.connect() as connection:
        remaining = schema_has_drift(connection)

    if remaining:
        raise RuntimeError(
            "Schema is still incomplete after alembic upgrade head:\n" + "\n".join(remaining)
        )

    logger.info("Alembic upgrade head completed (revision %s)", head)


def run_alembic_upgrade_head() -> None:
    """Apply migrations (upgrade or stamp when the legacy schema already matches)."""
    ensure_database_schema()

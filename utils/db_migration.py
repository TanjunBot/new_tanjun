from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

from alembic.config import Config

logger = logging.getLogger(__name__)

DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV = "DANGEROUSLY_DEBUG_PRINT_DATABASE_DONT_ENABLE"

_HOST_ENV_KEYS = ("TANJUN_TEST_DB_HOST", "database_ip", "DATABASE_IP", "MARIADB_HOST", "MYSQL_HOST")
_PORT_ENV_KEYS = ("TANJUN_TEST_DB_PORT", "database_port", "DATABASE_PORT", "MARIADB_PORT", "MYSQL_PORT")
_USER_ENV_KEYS = ("TANJUN_TEST_DB_USER", "database_user", "DATABASE_USER", "MARIADB_USER", "MYSQL_USER")
_PASSWORD_ENV_KEYS = (
    "TANJUN_TEST_DB_PASSWORD",
    "database_password",
    "DATABASE_PASSWORD",
    "MARIADB_PASSWORD",
    "MYSQL_PASSWORD",
)
_DATABASE_ENV_KEYS = (
    "TANJUN_TEST_DB_NAME",
    "database_schema",
    "DATABASE_SCHEMA",
    "MARIADB_DATABASE",
    "MYSQL_DATABASE",
)


@dataclass(frozen=True)
class DatabaseConnectionParams:
    host: str
    port: int
    user: str
    password: str
    database: str
    sources: dict[str, str]


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def dangerously_debug_print_database_enabled() -> bool:
    return _truthy_env(DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV)


def _first_env(*keys: str, default: str | None = None) -> str | None:
    value, _ = _first_env_with_source(*keys, default=default)
    return value


def _first_env_with_source(*keys: str, default: str | None = None) -> tuple[str | None, str | None]:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value, key
    return default, None


def _password_debug_label(password: str | None) -> str:
    if password is None:
        return "NOT SET"
    if password == "":
        return "SET (empty string)"
    return f"SET (length={len(password)})"


def resolve_database_connection_params() -> DatabaseConnectionParams:
    """Resolve host/port/user/password/database from env vars, then config.settings."""
    host, host_source = _first_env_with_source(*_HOST_ENV_KEYS)
    port_raw, port_source = _first_env_with_source(*_PORT_ENV_KEYS, default="3306")
    user, user_source = _first_env_with_source(*_USER_ENV_KEYS)
    password, password_source = _first_env_with_source(*_PASSWORD_ENV_KEYS)
    database, database_source = _first_env_with_source(*_DATABASE_ENV_KEYS)

    sources: dict[str, str] = {
        "host": host_source or "missing",
        "port": port_source or "default",
        "user": user_source or "missing",
        "password": password_source or "missing",
        "database": database_source or "missing",
    }

    if host is None or user is None or password is None or database is None:
        try:
            from config import settings

            if host is None:
                host = settings.database_ip
                sources["host"] = "config.settings.database_ip"
            port_before_settings = port_raw
            port_raw = str(port_raw or settings.database_port)
            if not port_source and str(port_before_settings or "") != str(port_raw):
                sources["port"] = "config.settings.database_port"
            if user is None:
                user = settings.database_user
                sources["user"] = "config.settings.database_user"
            if password is None:
                password = settings.database_password.get_secret_value()
                sources["password"] = "config.settings.database_password"
            if database is None:
                database = settings.database_schema
                sources["database"] = "config.settings.database_schema"
        except Exception:
            pass

    if host is None or user is None or password is None or database is None:
        raise RuntimeError(
            "Database credentials missing for migrations. Set database_* env vars or TANJUN_TEST_DB_*."
        )

    return DatabaseConnectionParams(
        host=str(host),
        port=int(port_raw or 3306),
        user=str(user),
        password=str(password),
        database=str(database),
        sources=sources,
    )


def format_database_connection_debug(
    params: DatabaseConnectionParams,
    *,
    context: str,
    extra: dict[str, Any] | None = None,
) -> str:
    url = (
        f"mysql+pymysql://{quote_plus(params.user)}:***@"
        f"{params.host}:{params.port}/{params.database}"
    )
    lines = [
        f"[{DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV}] {context}",
        f"  host={params.host!r} (from {params.sources['host']})",
        f"  port={params.port} (from {params.sources['port']})",
        f"  user={params.user!r} (from {params.sources['user']})",
        f"  password={_password_debug_label(params.password)} (from {params.sources['password']})",
        f"  database={params.database!r} (from {params.sources['database']})",
        f"  sqlalchemy_url={url}",
    ]
    for key in (
        *_HOST_ENV_KEYS,
        *_PORT_ENV_KEYS,
        *_USER_ENV_KEYS,
        *_PASSWORD_ENV_KEYS,
        *_DATABASE_ENV_KEYS,
    ):
        if key in os.environ:
            lines.append(f"  env_present[{key!r}]=yes")
    if extra:
        for name, value in extra.items():
            lines.append(f"  {name}={value!r}")
    return "\n".join(lines)


def log_database_connection_debug(
    *,
    context: str,
    log: logging.Logger | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    if not dangerously_debug_print_database_enabled():
        return
    try:
        params = resolve_database_connection_params()
    except Exception as exc:
        message = f"[{DANGEROUSLY_DEBUG_PRINT_DATABASE_ENV}] {context}\n  resolve_failed={exc!r}"
        if log is not None:
            log.warning(message)
        else:
            print(message, file=sys.stderr)
        return
    message = format_database_connection_debug(params, context=context, extra=extra)
    if log is not None:
        log.warning("%s", message)
    else:
        print(message, file=sys.stderr)


def get_database_url() -> str:
    """Build a SQLAlchemy URL for Alembic (sync PyMySQL driver)."""
    params = resolve_database_connection_params()
    safe_user = quote_plus(params.user)
    safe_password = quote_plus(params.password)
    return f"mysql+pymysql://{safe_user}:{safe_password}@{params.host}:{params.port}/{params.database}"


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
            f"Schema drift detected at Alembic head ({head}, {len(drift)} issue(s)). "
            "Add a repair migration instead of auto-repair:\n"
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

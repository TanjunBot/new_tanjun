from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Only patch config when running under pytest; conftest.py already loads this
# mock, but keeping the guard here prevents `alembic upgrade head` run from
# the shell (e.g. in CI) from replacing the real settings with a mock.
if "pytest" in sys.modules:
    try:
        import tests.mock_config as _mock_config

        _mock_config.patch_config_module()
    except ImportError:
        pass

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from utils.db_migration import get_database_url  # noqa: E402
from utils.schema_metadata import build_metadata  # noqa: E402

target_metadata = build_metadata()


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

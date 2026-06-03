"""Initial schema: all Tanjun tables from canonical DDL."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    from utils.migration_ddl import run_create_all_tables

    run_create_all_tables(op.get_bind())


def downgrade() -> None:
    from utils.migration_ddl import ordered_table_names

    for table_name in reversed(ordered_table_names()):
        op.execute(f"DROP TABLE IF EXISTS `{table_name}`")

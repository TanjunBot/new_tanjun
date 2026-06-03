"""Tests for safe startup schema migrations (schema_ensure)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from utils import schema_ensure  # noqa: E402

pytestmark = pytest.mark.unit


class TestSchemaEnsureHelpers:
    def test_extract_table_name_from_alter(self) -> None:
        assert schema_ensure.extract_table_name_from_alter("ALTER TABLE `foo` ADD COLUMN `x` INT") == "foo"
        assert schema_ensure.extract_table_name_from_alter("SELECT 1") is None

    def test_is_benign_migration_error(self) -> None:
        assert schema_ensure.is_benign_migration_error(Exception("Duplicate column name 'x'"))
        assert not schema_ensure.is_benign_migration_error(Exception("syntax error"))


class TestEnsureTableSchema:
    @pytest.mark.asyncio
    async def test_ensure_table_schema_from_table_def(self) -> None:
        from api import get_table_defs

        table_def = get_table_defs()["mediaChannel"]
        with (
            patch.object(schema_ensure, "ensure_columns_from_table_def", new=AsyncMock()) as ensure_cols,
            patch("api.get_table_defs", return_value={"mediaChannel": table_def}),
        ):
            await schema_ensure.ensure_table_schema("mediaChannel")
        ensure_cols.assert_awaited_once_with(table_def, None)

    @pytest.mark.asyncio
    async def test_ensure_table_schema_from_ddl_when_not_in_defs(self) -> None:
        ddl = "CREATE TABLE IF NOT EXISTS `legacy` (`id` INT)"
        with (
            patch("api.get_table_defs", return_value={}),
            patch("api.get_table_definitions", return_value={"legacy": ddl}),
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=False)),
            patch.object(schema_ensure, "ensure_table_from_ddl", new=AsyncMock()) as ensure_ddl,
        ):
            await schema_ensure.ensure_table_schema("legacy")
        ensure_ddl.assert_awaited_once_with(ddl, None)


class TestEnsureColumnsFromTableDef:
    @pytest.mark.asyncio
    async def test_adds_missing_columns(self) -> None:
        from api import get_table_defs

        table_def = get_table_defs()["mediaChannel"]
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=True)),
            patch.object(schema_ensure, "column_exists", new=AsyncMock(return_value=False)),
            patch("api.execute_action", new=AsyncMock(return_value=True)) as action,
        ):
            await schema_ensure.ensure_columns_from_table_def(table_def)
        assert action.await_count == len(table_def.columns)

    @pytest.mark.asyncio
    async def test_creates_table_when_absent(self) -> None:
        from api import get_table_defs

        table_def = get_table_defs()["mediaChannel"]
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=False)),
            patch.object(schema_ensure, "ensure_table_from_ddl", new=AsyncMock()) as ensure_ddl,
            patch("api.execute_action", new=AsyncMock()) as action,
        ):
            await schema_ensure.ensure_columns_from_table_def(table_def)
        ensure_ddl.assert_awaited_once()
        action.assert_not_awaited()


class TestRunAlterMigration:
    @pytest.mark.asyncio
    async def test_skips_when_table_missing_and_not_in_definitions(self) -> None:
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=False)),
            patch("api.get_table_definitions", return_value={}),
            patch("api.execute_action", new=AsyncMock()) as action,
        ):
            ok = await schema_ensure.run_alter_migration(
                "ALTER TABLE `missing_table` ADD COLUMN `x` INT",
                table_name="missing_table",
            )
        assert ok is False
        action.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_creates_table_from_definitions_when_missing(self) -> None:
        ddl = "CREATE TABLE IF NOT EXISTS `scheduledMessages` (`id` INT)"
        exists = AsyncMock(side_effect=[False, True])
        with (
            patch.object(schema_ensure, "table_exists", new=exists),
            patch("api.get_table_definitions", return_value={"scheduledMessages": ddl}),
            patch("api.execute_action", new=AsyncMock(return_value=True)) as action,
        ):
            ok = await schema_ensure.run_alter_migration(
                "ALTER TABLE `scheduledMessages` ADD COLUMN `attachments` TEXT",
                table_name="scheduledMessages",
            )
        assert ok is True
        create_calls = [c for c in action.await_args_list if "CREATE TABLE" in c.args[0]]
        assert len(create_calls) == 1

    @pytest.mark.asyncio
    async def test_duplicate_column_is_benign(self) -> None:
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=True)),
            patch(
                "api.execute_action",
                new=AsyncMock(side_effect=Exception("Duplicate column name 'attachments'")),
            ),
        ):
            ok = await schema_ensure.run_alter_migration(
                "ALTER TABLE `scheduledMessages` ADD COLUMN `attachments` TEXT",
                table_name="scheduledMessages",
            )
        assert ok is True

    @pytest.mark.asyncio
    async def test_unexpected_error_raises(self) -> None:
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=True)),
            patch("api.execute_action", new=AsyncMock(side_effect=Exception("syntax error"))),
            pytest.raises(Exception, match="syntax error"),
        ):
            await schema_ensure.run_alter_migration(
                "ALTER TABLE `level` ADD INDEX `idx` (`guild_id`)",
                table_name="level",
            )

    @pytest.mark.asyncio
    async def test_returns_false_when_execute_action_returns_none(self) -> None:
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=True)),
            patch("api.execute_action", new=AsyncMock(return_value=None)),
        ):
            ok = await schema_ensure.run_alter_migration(
                "ALTER TABLE `level` ADD INDEX `idx` (`guild_id`)",
                table_name="level",
            )
        assert ok is False


class TestMigrateReportsStatusColumns:
    @pytest.mark.asyncio
    async def test_adds_created_at_before_status_columns(self) -> None:
        column_checks: dict[str, bool] = {
            "created_at": False,
            "status": False,
            "status_updated_at": False,
            "status_updated_by": False,
        }

        async def col_exists(_table: str, column: str, bot=None) -> bool:
            return column_checks.get(column, True)

        executed: list[str] = []

        async def track_action(sql: str, *args, **kwargs) -> bool:
            executed.append(sql)
            if "ADD COLUMN `created_at`" in sql:
                column_checks["created_at"] = True
            if "ADD COLUMN `status`" in sql and "status_updated" not in sql:
                column_checks["status"] = True
            if "status_updated_at" in sql:
                column_checks["status_updated_at"] = True
            if "status_updated_by" in sql:
                column_checks["status_updated_by"] = True
            return True

        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=True)),
            patch.object(schema_ensure, "column_exists", side_effect=col_exists),
            patch("api.execute_action", side_effect=track_action),
        ):
            await schema_ensure.migrate_reports_status_columns()

        assert any("created_at" in sql for sql in executed)
        created_at_idx = next(i for i, sql in enumerate(executed) if "created_at" in sql)
        status_idx = next(i for i, sql in enumerate(executed) if "ADD COLUMN `status`" in sql)
        assert created_at_idx < status_idx

    @pytest.mark.asyncio
    async def test_skips_when_reports_table_absent(self) -> None:
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=False)),
            patch("api.get_table_definitions", return_value={}),
            patch("api.execute_action", new=AsyncMock()) as action,
        ):
            await schema_ensure.migrate_reports_status_columns()
        action.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_reports_still_missing_after_create_logs_and_returns(self) -> None:
        ddl = "CREATE TABLE IF NOT EXISTS `reports` (`id` INT)"
        with (
            patch.object(schema_ensure, "table_exists", new=AsyncMock(return_value=False)),
            patch("api.get_table_definitions", return_value={"reports": ddl}),
            patch.object(schema_ensure, "ensure_table_from_ddl", new=AsyncMock()),
            patch.object(schema_ensure, "run_alter_migration", new=AsyncMock()) as migrate,
        ):
            await schema_ensure.migrate_reports_status_columns()
        migrate.assert_not_awaited()


class TestRunStartupMigrations:
    @pytest.mark.asyncio
    async def test_does_not_raise_on_missing_table(self) -> None:
        with patch.object(schema_ensure, "run_alter_migration", new=AsyncMock(return_value=False)):
            await schema_ensure.run_startup_migrations()

    @pytest.mark.asyncio
    async def test_create_tables_invokes_alembic_upgrade(self) -> None:
        import api

        from api import get_table_definitions

        all_tables = [(name,) for name in get_table_definitions()]
        pool = MagicMock()
        conn = MagicMock()
        cursor = MagicMock()
        cursor.execute = AsyncMock()
        cursor.fetchall = AsyncMock(side_effect=[[("level",)], all_tables])
        cursor_cm = MagicMock()
        cursor_cm.__aenter__ = AsyncMock(return_value=cursor)
        cursor_cm.__aexit__ = AsyncMock(return_value=None)
        conn.cursor = MagicMock(return_value=cursor_cm)
        acquire_cm = MagicMock()
        acquire_cm.__aenter__ = AsyncMock(return_value=conn)
        acquire_cm.__aexit__ = AsyncMock(return_value=None)
        pool.acquire = MagicMock(return_value=acquire_cm)

        with (
            patch("api._get_pool", return_value=pool),
            patch("api.asyncio.wait_for", new=AsyncMock(return_value=conn)),
            patch("api.execute_action", new=AsyncMock(return_value=True)),
            patch("utils.db_migration.ensure_database_schema") as migrations,
        ):
            await api.create_tables()

        migrations.assert_called_once()

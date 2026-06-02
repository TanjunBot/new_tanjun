"""Tests for safe startup schema migrations (schema_ensure)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from utils import schema_ensure  # noqa: E402

pytestmark = pytest.mark.unit


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


class TestRunStartupMigrations:
    @pytest.mark.asyncio
    async def test_does_not_raise_on_missing_table(self) -> None:
        with patch.object(schema_ensure, "run_alter_migration", new=AsyncMock(return_value=False)):
            await schema_ensure.run_startup_migrations()

    @pytest.mark.asyncio
    async def test_create_tables_invokes_startup_migrations(self) -> None:
        import api

        pool = AsyncMock()
        conn = AsyncMock()
        cursor = AsyncMock()
        cursor.fetchall = AsyncMock(return_value=[("level",), ("warnings",)])
        cursor_cm = AsyncMock()
        cursor_cm.__aenter__ = AsyncMock(return_value=cursor)
        cursor_cm.__aexit__ = AsyncMock(return_value=None)
        conn.cursor = MagicMock(return_value=cursor_cm)
        pool.acquire = AsyncMock(return_value=conn)

        with (
            patch("api._get_pool", return_value=pool),
            patch("api.execute_action", new=AsyncMock(return_value=True)),
            patch("utils.schema_ensure.run_startup_migrations", new=AsyncMock()) as migrations,
        ):
            await api.create_tables()

        migrations.assert_awaited_once()

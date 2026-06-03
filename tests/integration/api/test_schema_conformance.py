"""Integration tests: Alembic migrations produce the canonical schema."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

_LEGACY_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "schema_legacy"


@pytest.fixture(autouse=True)
def _restore_schema_head_after_test() -> None:
    yield
    from alembic import command

    command.upgrade(_migration_config(), "head")


def _migration_config():
    from alembic.config import Config

    from utils.db_migration import get_database_url

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", get_database_url())
    return cfg


def _rerun_migrations_from(revision: str) -> None:
    from alembic import command

    cfg = _migration_config()
    command.stamp(cfg, revision)
    command.upgrade(cfg, "head")


async def test_schema_conformance_after_alembic_upgrade(integration_db_pool) -> None:
    from utils.schema_conformance import assert_schema_conformance

    await assert_schema_conformance(integration_db_pool)


async def test_ensure_database_schema_stamps_untracked_full_schema(integration_db_pool) -> None:
    from alembic.script import ScriptDirectory

    from utils.db_migration import ensure_database_schema
    from utils.schema_conformance import assert_schema_conformance

    pool = integration_db_pool
    await assert_schema_conformance(pool)

    cfg = _migration_config()
    head = ScriptDirectory.from_config(cfg).get_current_head()

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS alembic_version")
        await conn.commit()

    ensure_database_schema()

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("SELECT version_num FROM alembic_version LIMIT 1")
        row = await cursor.fetchone()

    assert row is not None
    assert row[0] == head


async def test_ensure_database_schema_idempotent(integration_db_pool) -> None:
    from utils.db_migration import ensure_database_schema
    from utils.schema_conformance import assert_schema_conformance

    pool = integration_db_pool

    ensure_database_schema()
    ensure_database_schema()
    await assert_schema_conformance(pool)


async def test_legacy_giveaway_schema_upgrades_to_current(integration_db_pool) -> None:
    pool = integration_db_pool
    legacy_sql = (_LEGACY_DIR / "giveaway_without_giveaway_id.sql").read_text(encoding="utf-8")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS `giveaway`")
        await cursor.execute(legacy_sql)
        await conn.commit()

    _rerun_migrations_from("001_initial_schema")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'giveaway' AND column_name = 'giveaway_id'"
        )
        row = await cursor.fetchone()
    assert row and row[0] == 1


async def test_legacy_giveaway_with_id_auto_pk_upgrades_to_current(integration_db_pool) -> None:
    pool = integration_db_pool
    legacy_sql = (_LEGACY_DIR / "giveaway_with_id_auto_pk.sql").read_text(encoding="utf-8")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS `giveaway`")
        await cursor.execute(legacy_sql)
        await cursor.execute(
            "INSERT INTO `giveaway` (`guild_id`, `title`, `endtime`) VALUES "
            "('111', 'legacy', '2030-01-01 00:00:00'), "
            "('222', 'legacy2', '2031-01-01 00:00:00')"
        )
        await conn.commit()

    _rerun_migrations_from("001_initial_schema")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute(
            "SELECT column_name, extra FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'giveaway' "
            "AND column_name IN ('giveaway_id', 'id')"
        )
        rows = {row[0]: row[1] for row in await cursor.fetchall()}
        await cursor.execute("SELECT `giveaway_id`, `guild_id` FROM `giveaway` ORDER BY `giveaway_id`")
        data = await cursor.fetchall()

    assert "giveaway_id" in rows
    assert "auto_increment" in rows["giveaway_id"].lower()
    assert "id" not in rows
    assert data == [(1, "111"), (2, "222")]


async def test_legacy_reports_gets_status_columns(integration_db_pool) -> None:
    from utils.schema_conformance import fetch_existing_columns

    pool = integration_db_pool
    legacy_sql = (_LEGACY_DIR / "reports_minimal.sql").read_text(encoding="utf-8")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS `report_evidence`")
        await cursor.execute("DROP TABLE IF EXISTS `report_mod_actions`")
        await cursor.execute("DROP TABLE IF EXISTS `reports`")
        await cursor.execute(legacy_sql)
        await conn.commit()

    _rerun_migrations_from("001_initial_schema")
    columns = await fetch_existing_columns(pool)
    report_cols = columns.get("reports", set())
    assert "status" in report_cols
    assert "created_at" in report_cols

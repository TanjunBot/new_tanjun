"""Integration tests: Alembic migrations produce the canonical schema."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

import pytest
from asyncmy.errors import OperationalError

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

_LEGACY_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "schema_legacy"


@pytest.fixture(autouse=True)
def _restore_schema_head_after_test() -> None:
    yield
    from utils.db_migration import ensure_database_schema

    ensure_database_schema()


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


async def _run_with_schema_retry(fn: Callable[[], Awaitable[None]], *, attempts: int = 5) -> None:
    for attempt in range(attempts):
        try:
            await fn()
            return
        except OperationalError as exc:
            if exc.args[0] != 1412 or attempt == attempts - 1:
                raise
            await asyncio.sleep(0.2 * (attempt + 1))


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

    await pool.clear()
    _rerun_migrations_from("001_initial_schema")
    await pool.clear()

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
    assert list(data) == [(1, "111"), (2, "222")]


async def test_legacy_trigger_messages_guild_id_column_upgrades(integration_db_pool) -> None:
    pool = integration_db_pool
    legacy_sql = (_LEGACY_DIR / "trigger_messages_guild_id.sql").read_text(encoding="utf-8")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS `triggerMessagesChannel`")
        await cursor.execute("DROP TABLE IF EXISTS `triggerMessages`")
        for statement in legacy_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                await cursor.execute(stmt)
        await cursor.execute(
            "INSERT INTO `triggerMessages` (`guildId`, `trigger`, `response`) VALUES ('999', 'hi', 'bye')"
        )
        await cursor.execute(
            "INSERT INTO `triggerMessagesChannel` (`guild_id`, `channel_id`, `triggerId`) "
            "VALUES ('999', '111', 1)"
        )
        await conn.commit()

    _rerun_migrations_from("003_giveaway_legacy_column")

    async def _verify() -> None:
        async with pool.acquire() as conn, conn.cursor() as cursor:
            await cursor.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = 'triggerMessages' "
                "AND column_name IN ('guild_id', 'guildId')"
            )
            cols = {row[0] for row in await cursor.fetchall()}
            await cursor.execute(
                "SELECT is_nullable FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = 'triggerMessages' AND column_name = 'guild_id'"
            )
            nullable = await cursor.fetchone()
            await cursor.execute(
                "SELECT COUNT(DISTINCT index_name) FROM information_schema.statistics "
                "WHERE table_schema = DATABASE() AND table_name = 'triggerMessages' "
                "AND index_name = 'uk_guild_id' AND non_unique = 0"
            )
            uk = await cursor.fetchone()
            await cursor.execute("SELECT `guild_id` FROM `triggerMessages` WHERE `id` = 1")
            row = await cursor.fetchone()

        assert cols == {"guild_id"}
        assert nullable and nullable[0] == "NO"
        assert uk and uk[0] == 1
        assert row == ("999",)

    await _run_with_schema_retry(_verify)


async def test_legacy_camelcase_columns_renamed(integration_db_pool) -> None:
    pool = integration_db_pool
    legacy_sql = (_LEGACY_DIR / "legacy_camelcase_columns.sql").read_text(encoding="utf-8")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS `autopublish`")
        await cursor.execute("DROP TABLE IF EXISTS `afkMessages`")
        for statement in legacy_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                await cursor.execute(stmt)
        await conn.commit()

    _rerun_migrations_from("004_schema_fk_and_guild_keys")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'afkMessages' "
            "AND column_name IN ('user_id', 'channel_id', 'messageId', 'userId', 'channelId')"
        )
        afk_cols = {row[0] for row in await cursor.fetchall()}
        await cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'autopublish' "
            "AND column_name IN ('channel_id', 'channelId')"
        )
        auto_cols = {row[0] for row in await cursor.fetchall()}

    assert afk_cols == {"user_id", "channel_id", "messageId"}
    assert auto_cols == {"channel_id"}


async def test_giveaway_nullable_id_repaired_at_head(integration_db_pool) -> None:
    pool = integration_db_pool
    legacy_sql = (_LEGACY_DIR / "giveaway_nullable_id_with_legacy_pk.sql").read_text(encoding="utf-8")

    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS `giveaway`")
        for statement in legacy_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                await cursor.execute(stmt)
        await conn.commit()

    cfg = _migration_config()
    from alembic import command

    command.stamp(cfg, "004_schema_fk_and_guild_keys")
    command.upgrade(cfg, "006_giveaway_id_not_null")

    async def _verify() -> None:
        async with pool.acquire() as conn, conn.cursor() as cursor:
            await cursor.execute(
                "SELECT column_name, extra, is_nullable FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = 'giveaway' "
                "AND column_name IN ('giveaway_id', 'giveawayId', 'id')"
            )
            rows = {row[0]: (row[1], row[2]) for row in await cursor.fetchall()}
            await cursor.execute("SELECT `giveaway_id`, `guild_id` FROM `giveaway` WHERE `giveaway_id` = 7")
            data = await cursor.fetchone()

        assert "giveaway_id" in rows
        assert rows["giveaway_id"][1] == "NO"
        assert "auto_increment" in rows["giveaway_id"][0].lower()
        assert "giveawayId" not in rows
        assert data == (7, "111")

    await _run_with_schema_retry(_verify)


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

    cfg = _migration_config()
    from alembic import command

    command.stamp(cfg, "001_initial_schema")
    command.upgrade(cfg, "002_legacy_schema_patches")
    columns = await fetch_existing_columns(pool)
    report_cols = columns.get("reports", set())
    assert "status" in report_cols
    assert "created_at" in report_cols
